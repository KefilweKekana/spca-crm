from datetime import timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now, time_diff_in_hours


class CrueltyReport(Document):
    def before_insert(self):
        self.case_id = self.name
        if not self.report_date:
            self.report_date = frappe.utils.today()
        self.set_sla_due_dates()

    def validate(self):
        self.case_id = self.name
        self.calculate_animal_count()
        self.validate_priority()
        self.set_resolution_timestamps()
        self.set_sla_breached()
        self.calculate_case_age()
        self.calculate_timings()
        self.log_status_change()
        self.log_assignment_change()

    def on_update(self):
        self.notify_assignment()

    def set_sla_due_dates(self):
        """Set response and resolution due dates based on priority."""
        now_dt = get_datetime(now())
        sla_map = {
            "Critical": {"response": 1, "resolution": 24},
            "High": {"response": 4, "resolution": 72},
            "Medium": {"response": 24, "resolution": 168},
            "Low": {"response": 48, "resolution": 336},
        }
        sla = sla_map.get(self.priority, {"response": 24, "resolution": 168})

        self.first_response_due = now_dt + timedelta(hours=sla["response"])
        self.resolution_due = now_dt + timedelta(hours=sla["resolution"])

    def calculate_animal_count(self):
        self.animal_count = sum(
            (row.quantity or 1) for row in self.get("animals_involved", [])
        )

    def validate_priority(self):
        if self.is_urgent and self.priority not in ("High", "Critical"):
            self.priority = "High"

    def set_resolution_timestamps(self):
        if self.status == "Resolved" and not self.resolved_at:
            self.resolved_at = now()
            self.resolved_by = frappe.session.user
        if self.status == "Closed" and not self.closed_at:
            self.closed_at = now()
            self.closed_by = frappe.session.user

    def set_sla_breached(self):
        now_dt = get_datetime(now())
        breached = False

        if self.first_response_due and not self.first_responded_at:
            breached = now_dt > get_datetime(self.first_response_due)
        if self.resolution_due and self.status not in ("Resolved", "Closed"):
            if now_dt > get_datetime(self.resolution_due):
                breached = True

        self.sla_breached = 1 if breached else 0

    def calculate_case_age(self):
        if self.report_date:
            self.case_age_days = (
                frappe.utils.getdate() - frappe.utils.getdate(self.report_date)
            ).days

    def calculate_timings(self):
        if self.first_responded_at and self.report_date:
            self.response_time_hours = round(
                time_diff_in_hours(
                    get_datetime(self.first_responded_at),
                    get_datetime(self.report_date),
                ),
                2,
            )
        if self.resolved_at and self.report_date:
            self.resolution_time_hours = round(
                time_diff_in_hours(
                    get_datetime(self.resolved_at),
                    get_datetime(self.report_date),
                ),
                2,
            )

    def log_status_change(self):
        previous = self.get_doc_before_save()
        if not previous:
            return
        old_status = previous.status
        if old_status != self.status:
            self.add_case_note(
                note_type="Internal",
                note=f"Status changed from <b>{old_status}</b> to <b>{self.status}</b>.",
            )
            if self.status == "Assigned" and not self.assigned_inspector:
                frappe.throw(
                    _("Please assign an inspector before setting status to Assigned.")
                )

    def log_assignment_change(self):
        previous = self.get_doc_before_save()
        if not previous:
            return
        if previous.assigned_inspector != self.assigned_inspector and self.assigned_inspector:
            self.add_case_note(
                note_type="Internal",
                note=f"Case assigned to <b>{self.assigned_inspector}</b>.",
            )

    def notify_assignment(self):
        previous = self.get_doc_before_save()
        if not previous:
            return
        if previous.assigned_inspector != self.assigned_inspector and self.assigned_inspector:
            self.send_notification(
                recipient=self.assigned_inspector,
                subject=f"Cruelty Case {self.name} assigned to you",
                message=f"""
                <p>A new cruelty case has been assigned to you:</p>
                <ul>
                    <li><b>Case ID:</b> {self.name}</li>
                    <li><b>Priority:</b> {self.priority}</li>
                    <li><b>Location:</b> {self.location or 'N/A'}</li>
                    <li><b>SLA:</b> First response due by {self.first_response_due}</li>
                </ul>
                """,
            )

    def add_case_note(self, note_type, note):
        self.append(
            "case_notes",
            {
                "note_datetime": now(),
                "user": frappe.session.user,
                "note_type": note_type,
                "note": note,
            },
        )

    def send_notification(self, recipient, subject, message):
        if not recipient:
            return
        try:
            frappe.sendmail(
                recipients=[recipient],
                subject=subject,
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name,
            )
        except Exception:
            frappe.log_error(
                title="SPCA Helpdesk Notification Failed",
                message=frappe.get_traceback(),
            )


def before_insert(doc, method=None):
    pass


def validate(doc, method=None):
    pass


def on_update(doc, method=None):
    pass


def on_submit(doc, method=None):
    pass


@frappe.whitelist()
def mark_first_response(case_name):
    """Call from client script when inspector first opens/acts on case."""
    case = frappe.get_doc("Cruelty Report", case_name)
    if not case.first_responded_at:
        case.first_responded_at = now()
        case.save(ignore_permissions=True)
    return case.first_responded_at


@frappe.whitelist()
def assign_inspector(case_name, inspector, set_status=1):
    case = frappe.get_doc("Cruelty Report", case_name)
    case.assigned_inspector = inspector or None
    if set_status and inspector:
        case.status = "Assigned"
    elif not inspector:
        case.status = "Draft"
    case.save(ignore_permissions=True)
    return case


@frappe.whitelist()
def get_inspector_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """
        SELECT u.name, u.full_name
        FROM `tabUser` u
        INNER JOIN `tabHas Role` r ON r.parent = u.name
        WHERE r.role = 'SPCA Inspector'
            AND u.enabled = 1
            AND u.name LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
        """,
        {"txt": f"%{txt}%", "start": start, "page_len": page_len},
    )


@frappe.whitelist()
def escalate_case(case_name, reason):
    case = frappe.get_doc("Cruelty Report", case_name)
    case.status = "Escalated"
    case.add_case_note(note_type="Internal", note=f"Escalated: {reason}")
    case.save(ignore_permissions=True)
    return case


def notify_overdue_reports():
    """Scheduled hourly: notify managers of cases approaching or breaching SLA."""
    overdue = frappe.get_all(
        "Cruelty Report",
        filters={
            "status": ["not in", ["Resolved", "Closed"]],
            "sla_breached": 1,
        },
        fields=[
            "name",
            "priority",
            "assigned_inspector",
            "first_response_due",
            "resolution_due",
        ],
    )

    managers = frappe.get_all(
        "Has Role",
        filters={"role": "SPCA Manager", "parenttype": "User"},
        pluck="parent",
    )
    if not managers:
        return

    for case in overdue:
        subject = f"SLA Breach Alert: Cruelty Case {case.name}"
        message = f"""
        <p>Cruelty case <b>{case.name}</b> has breached SLA.</p>
        <ul>
            <li><b>Priority:</b> {case.priority}</li>
            <li><b>Inspector:</b> {case.assigned_inspector or 'Unassigned'}</li>
            <li><b>First Response Due:</b> {case.first_response_due}</li>
            <li><b>Resolution Due:</b> {case.resolution_due}</li>
        </ul>
        """
        try:
            frappe.sendmail(recipients=managers, subject=subject, message=message)
        except Exception:
            frappe.log_error(title="SPCA SLA Alert Failed")


def auto_close_resolved_cases():
    """Scheduled daily: close cases that have been Resolved for 7+ days."""
    cutoff = frappe.utils.add_days(frappe.utils.nowdate(), -7)
    resolved = frappe.get_all(
        "Cruelty Report",
        filters={"status": "Resolved", "resolved_at": ["<", cutoff]},
        pluck="name",
    )
    for name in resolved:
        case = frappe.get_doc("Cruelty Report", name)
        case.status = "Closed"
        case.closed_at = now()
        case.closed_by = "System"
        case.closure_reason = "Auto-closed after 7 days in Resolved status."
        case.add_case_note(
            note_type="Internal",
            note="Case automatically closed after 7 days in Resolved status.",
        )
        case.save(ignore_permissions=True)
