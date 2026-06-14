import json
import os

import frappe


ROLES = [
    "SPCA Inspector",
    "SPCA Call Operator",
    "SPCA Manager",
]


def after_install():
    create_roles()
    create_default_branch()
    create_default_settings()
    load_fixtures()


def after_migrate():
    create_roles()
    create_default_settings()
    load_fixtures()


def create_roles():
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert()


def create_default_branch():
    if not frappe.db.exists("SPCA Branch", "Tshwane"):
        branch = frappe.new_doc("SPCA Branch")
        branch.branch_name = "Tshwane"
        branch.branch_code = "TSH"
        branch.city = "Pretoria"
        branch.province = "Gauteng"
        branch.is_active = 1
        branch.insert(ignore_permissions=True)


def create_default_settings():
    if not frappe.db.exists("SPCA CRM Settings", "SPCA CRM Settings"):
        settings = frappe.new_doc("SPCA CRM Settings")
        settings.web_form_doctype = "Cruelty_Form"
        settings.webform_route = "report"
        settings.allow_anonymous_reports = 1
        settings.auto_convert_submissions = 1
        settings.role_allowed_to_convert = "SPCA Manager"
        settings.default_priority = "Medium"
        settings.save(ignore_permissions=True)


def load_fixtures():
    """Load static fixture JSON files bundled with the app."""
    fixture_dir = frappe.get_app_path("spca_crm", "spca_crm", "fixtures")
    if not os.path.exists(fixture_dir):
        return

    fixture_files = [
        "workflow_cruelty_report.json",
        "notification_cruelty_report.json",
        "workspace_spca_crm.json",
        "dashboard_chart_cases_by_status.json",
        "dashboard_chart_cases_by_priority.json",
        "dashboard_chart_monthly_trend.json",
        "number_cards.json",
        "web_form_public_cruelty_report.json",
    ]

    for filename in fixture_files:
        filepath = os.path.join(fixture_dir, filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for doc in data:
            if frappe.db.exists(doc["doctype"], doc["name"]):
                continue
            try:
                frappe.get_doc(doc).insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(title=f"SPCA Fixture Load Failed: {filename}")
