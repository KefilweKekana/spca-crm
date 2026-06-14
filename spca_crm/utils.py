import re

import frappe
from frappe import _


def format_case_id(case_id: str) -> str:
    """Return a human-friendly case reference."""
    return case_id.upper() if case_id else ""


def parse_gps_coordinates(coordinates: str):
    """Parse 'lat, lng' string into a tuple."""
    if not coordinates:
        return None
    match = re.match(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$", coordinates)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None


def get_user_branch(user=None):
    user = user or frappe.session.user
    branch = frappe.db.get_value("SPCA Branch", {"manager": user}, "name")
    return branch


def create_cruelty_report_from_webform(source_doc, skip_permission_check=False):
    """Convert a web form submission (any DocType) into a Cruelty Report.

    source_doc can be a dict or a Frappe Document.
    """
    settings = frappe.get_doc("SPCA CRM Settings", "SPCA CRM Settings")
    if not settings.auto_convert_submissions:
        return None

    if not skip_permission_check:
        _check_conversion_permission(settings)

    data = source_doc.as_dict() if hasattr(source_doc, "as_dict") else dict(source_doc)
    report = frappe.new_doc("Cruelty Report")

    # Defaults
    report.report_received_via = "Web Form"
    report.priority = data.get("priority") or settings.default_priority or "Medium"
    report.branch = data.get("branch") or settings.default_branch
    if not report.branch:
        report.branch = frappe.db.get_value("SPCA Branch", {"is_active": 1}, "name")

    # Apply configured field mapping
    mapping = settings.field_mapping or get_default_field_mapping()
    for row in mapping:
        value = data.get(row.source_field) or row.default_value
        if value and hasattr(report, row.target_field):
            setattr(report, row.target_field, value)

    # Handle complainant
    is_anonymous = bool(
        data.get("is_anonymous") or data.get("anonymous") or data.get("report_anonymously")
    )
    report.is_anonymous = 1 if is_anonymous else 0

    if not report.is_anonymous:
        complainant = get_or_create_complainant(data)
        if complainant:
            report.complainant = complainant

    # Auto-assign if configured
    if settings.auto_assign_to and not report.assigned_inspector:
        report.assigned_inspector = settings.auto_assign_to
        report.status = "Assigned"

    # Ensure required fields
    if not report.allegation_description:
        report.allegation_description = data.get("description") or data.get("message") or ""
    if not report.location:
        report.location = data.get("location") or data.get("address") or ""

    report.insert(ignore_permissions=True)

    # Link back to source doc (only if the custom fields exist on source DocType)
    try:
        source_name = data.get("name")
        if source_name:
            meta = frappe.get_meta(settings.web_form_doctype)
            updates = {}
            if meta.has_field("spca_cruelty_report"):
                updates["spca_cruelty_report"] = report.name
            if meta.has_field("spca_conversion_status"):
                updates["spca_conversion_status"] = "Converted"
            if updates:
                frappe.db.set_value(settings.web_form_doctype, source_name, updates)
    except Exception:
        frappe.log_error(title="SPCA Webform Linkback Failed")

    return report.name


def _check_conversion_permission(settings):
    required_role = settings.role_allowed_to_convert or "SPCA Manager"
    if required_role and required_role not in frappe.get_roles():
        frappe.throw(_("You do not have permission to convert web form submissions."))


def get_default_field_mapping():
    """Default mapping for a typical Cruelty_Form DocType."""
    return [
        {"source_field": "location", "target_field": "location"},
        {"source_field": "suburb", "target_field": "suburb"},
        {"source_field": "city", "target_field": "city"},
        {"source_field": "province", "target_field": "province"},
        {"source_field": "gps_coordinates", "target_field": "gps_coordinates"},
        {"source_field": "suspected_violation", "target_field": "suspected_violation"},
        {"source_field": "allegation_description", "target_field": "allegation_description"},
        {"source_field": "description", "target_field": "allegation_description"},
        {"source_field": "priority", "target_field": "priority"},
        {"source_field": "incident_date", "target_field": "incident_date"},
        {"source_field": "incident_time", "target_field": "incident_time"},
        {"source_field": "is_anonymous", "target_field": "is_anonymous"},
    ]


def get_or_create_complainant(data: dict) -> str:
    phone = (data.get("complainant_phone") or data.get("phone") or "").strip()
    email = (data.get("complainant_email") or data.get("email") or "").strip()
    name = data.get("complainant_name") or data.get("full_name") or data.get("name")

    filters = {}
    if phone:
        filters["phone"] = phone
    elif email:
        filters["email"] = email
    else:
        return None

    existing = frappe.db.get_value("Complainant", filters, "name")
    if existing:
        return existing

    complainant = frappe.new_doc("Complainant")
    complainant.first_name = name or "Anonymous"
    complainant.phone = phone
    complainant.email = email
    complainant.preferred_contact = data.get("preferred_contact", "Phone")
    complainant.insert(ignore_permissions=True)
    return complainant.name


@frappe.whitelist()
def convert_webform_to_case(source_doctype, source_name):
    """Manual conversion whitelist for users with permission."""
    settings = frappe.get_doc("SPCA CRM Settings", "SPCA CRM Settings")
    _check_conversion_permission(settings)

    if source_doctype != settings.web_form_doctype:
        frappe.throw(_("Source DocType does not match configured web form DocType."))

    source_doc = frappe.get_doc(source_doctype, source_name)
    case_id = create_cruelty_report_from_webform(source_doc, skip_permission_check=False)
    return {"cruelty_report": case_id}
