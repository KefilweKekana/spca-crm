from frappe.model.document import Document


class SPCAHelpdeskSettings(Document):
    def validate(self):
        if not self.web_form_doctype:
            self.web_form_doctype = "Cruelty_Form"
        if not self.default_priority:
            self.default_priority = "Medium"
