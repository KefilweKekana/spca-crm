import unittest

import frappe

from spca_crm.doctype.cruelty_report.cruelty_report import assign_inspector


class TestCrueltyReport(unittest.TestCase):
    def setUp(self):
        self.branch = "Tshwane"
        if not frappe.db.exists("SPCA Branch", self.branch):
            branch = frappe.new_doc("SPCA Branch")
            branch.branch_name = self.branch
            branch.branch_code = "TSH"
            branch.city = "Pretoria"
            branch.province = "Gauteng"
            branch.is_active = 1
            branch.insert(ignore_permissions=True)

    def test_create_cruelty_report(self):
        report = frappe.new_doc("Cruelty Report")
        report.report_received_via = "Phone"
        report.priority = "High"
        report.location = "123 Main St"
        report.branch = self.branch
        report.allegation_description = "Test allegation"
        report.insert(ignore_permissions=True)

        self.assertTrue(report.name)
        self.assertEqual(report.status, "Draft")
        self.assertTrue(report.first_response_due)
        self.assertTrue(report.resolution_due)

    def test_assign_inspector(self):
        report = frappe.new_doc("Cruelty Report")
        report.report_received_via = "Email"
        report.priority = "Medium"
        report.location = "456 Oak Ave"
        report.branch = self.branch
        report.allegation_description = "Test"
        report.insert(ignore_permissions=True)

        assign_inspector(report.name, "Administrator")
        report.reload()
        self.assertEqual(report.status, "Assigned")
        self.assertEqual(report.assigned_inspector, "Administrator")
