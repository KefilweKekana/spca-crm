import json

import frappe
from frappe import _


@frappe.whitelist()
def bulk_assign_inspector(case_names, inspector):
    if not frappe.has_permission("Cruelty Report", "write"):
        frappe.throw(_("Not permitted to assign cases."))

    names = json.loads(case_names)
    for name in names:
        case = frappe.get_doc("Cruelty Report", name)
        case.assigned_inspector = inspector
        case.status = "Assigned"
        case.save(ignore_permissions=True)

    return {"assigned": len(names)}
