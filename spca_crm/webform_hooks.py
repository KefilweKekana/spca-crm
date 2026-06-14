import frappe

from spca_crm.utils import create_cruelty_report_from_webform


def on_cruelty_form_after_insert(doc, method=None):
    """Doc event hook for the configured public web form DocType.

    Add this to hooks.py:
        doc_events = {
            "Cruelty_Form": {
                "after_insert": "spca_crm.webform_hooks.on_cruelty_form_after_insert"
            }
        }
    """
    settings = frappe.get_doc("SPCA CRM Settings", "SPCA CRM Settings")
    if doc.doctype != settings.web_form_doctype:
        return
    if not settings.auto_convert_submissions:
        return
    try:
        create_cruelty_report_from_webform(doc, skip_permission_check=True)
    except Exception:
        frappe.log_error(title="SPCA Web Form Auto-Conversion Failed")
