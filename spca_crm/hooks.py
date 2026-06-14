from . import __version__ as app_version

app_name = "spca_crm"
app_title = "SPCA CRM"
app_publisher = "SPCA Digital Team"
app_description = "ERPNext CRM module for SPCA cruelty report management, inspections and case workflow."
app_email = "dev@spca.org.za"
app_license = "MIT"
app_version = app_version

required_apps = ["erpnext"]

# ------------------ Fixtures ------------------
fixtures = [
    "SPCA CRM Settings",
    {
        "dt": "Workflow",
        "filters": [["document_type", "in", ["Cruelty Report"]]],
    },
    {
        "dt": "Workflow State",
        "filters": [
            ["name", "in", ["Draft", "Assigned", "In Progress", "Escalated", "Resolved", "Closed", "Reopened"]]
        ],
    },
    {
        "dt": "Notification",
        "filters": [["document_type", "in", ["Cruelty Report"]]],
    },
    "Workspace",
    "Dashboard Chart",
    "Number Card",
]

# ------------------ DocType Events ------------------
doc_events = {
    "Cruelty Report": {
        "before_insert": "spca_crm.doctype.cruelty_report.cruelty_report.before_insert",
        "validate": "spca_crm.doctype.cruelty_report.cruelty_report.validate",
        "on_update": "spca_crm.doctype.cruelty_report.cruelty_report.on_update",
        "on_submit": "spca_crm.doctype.cruelty_report.cruelty_report.on_submit",
    },
    "Cruelty_Form": {
        "after_insert": "spca_crm.webform_hooks.on_cruelty_form_after_insert",
    },
}

# ------------------ Custom JS ------------------
doctype_js = {
    "Cruelty_Form": "spca_crm/client_scripts/cruelty_form.js",
}

# ------------------ Scheduled Tasks ------------------
scheduler_events = {
    "hourly": [
        "spca_crm.doctype.cruelty_report.cruelty_report.notify_overdue_reports",
    ],
    "daily": [
        "spca_crm.doctype.cruelty_report.cruelty_report.auto_close_resolved_cases",
    ],
}

# ------------------ Jinja Filters / Includes ------------------
jinja = {
    "methods": [
        "spca_crm.utils.format_case_id",
    ]
}

# ------------------ Setup Wizard / After Install ------------------
after_install = "spca_crm.setup.install.after_install"
after_migrate = "spca_crm.setup.install.after_migrate"
