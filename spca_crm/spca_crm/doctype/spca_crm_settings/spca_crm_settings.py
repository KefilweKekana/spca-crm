import frappe
from frappe.model.document import Document


class SPCACRMSettings(Document):
    def validate(self):
        if not self.web_form_doctype:
            self.web_form_doctype = "Cruelty_Form"
        if not self.default_priority:
            self.default_priority = "Medium"

    @staticmethod
    def get():
        if not frappe.db.exists("SPCA CRM Settings", "SPCA CRM Settings"):
            return frappe.new_doc("SPCA CRM Settings")
        return frappe.get_cached_doc("SPCA CRM Settings", "SPCA CRM Settings")
