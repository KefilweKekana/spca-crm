from frappe.model.document import Document


class Complainant(Document):
    def validate(self):
        if self.phone:
            self.phone = self.phone.strip()
