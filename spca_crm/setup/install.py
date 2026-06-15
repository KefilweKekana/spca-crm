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


def after_migrate():
    create_roles()
    create_default_settings()


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
    if not frappe.db.exists("SPCA Helpdesk Settings", "SPCA Helpdesk Settings"):
        settings = frappe.new_doc("SPCA Helpdesk Settings")
        settings.web_form_doctype = "Cruelty_Form"
        settings.webform_route = "report"
        settings.allow_anonymous_reports = 1
        settings.auto_convert_submissions = 1
        settings.role_allowed_to_convert = "SPCA Manager"
        settings.default_priority = "Medium"
        settings.save(ignore_permissions=True)
