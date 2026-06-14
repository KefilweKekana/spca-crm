import frappe


def execute(filters=None):
    columns = [
        {"fieldname": "inspector", "label": "Inspector", "fieldtype": "Link", "options": "User", "width": 200},
        {"fieldname": "total_cases", "label": "Total Cases", "fieldtype": "Int", "width": 120},
        {"fieldname": "open_cases", "label": "Open Cases", "fieldtype": "Int", "width": 120},
        {"fieldname": "resolved_cases", "label": "Resolved", "fieldtype": "Int", "width": 120},
        {"fieldname": "sla_breached", "label": "SLA Breached", "fieldtype": "Int", "width": 140},
        {"fieldname": "avg_resolution_hours", "label": "Avg Resolution (hrs)", "fieldtype": "Float", "width": 160},
    ]

    data = frappe.db.sql(
        """
        SELECT
            assigned_inspector AS inspector,
            COUNT(*) AS total_cases,
            SUM(CASE WHEN status NOT IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS open_cases,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_cases,
            SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) AS sla_breached,
            AVG(CASE WHEN resolution_time_hours > 0 THEN resolution_time_hours END) AS avg_resolution_hours
        FROM `tabCruelty Report`
        WHERE assigned_inspector IS NOT NULL
        GROUP BY assigned_inspector
        ORDER BY open_cases DESC
        """,
        as_dict=True,
    )

    return columns, data
