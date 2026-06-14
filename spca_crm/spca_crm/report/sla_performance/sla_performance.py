import frappe


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"fieldname": "priority", "label": "Priority", "fieldtype": "Data", "width": 120},
        {"fieldname": "total_cases", "label": "Total Cases", "fieldtype": "Int", "width": 120},
        {"fieldname": "responded_on_time", "label": "Responded On Time", "fieldtype": "Int", "width": 160},
        {"fieldname": "resolved_on_time", "label": "Resolved On Time", "fieldtype": "Int", "width": 160},
        {"fieldname": "breached", "label": "SLA Breached", "fieldtype": "Int", "width": 140},
        {"fieldname": "avg_response_hours", "label": "Avg Response (hrs)", "fieldtype": "Float", "width": 160},
    ]

    conditions = ""
    values = {}
    if filters.get("from_date"):
        conditions += " AND report_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND report_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    data = frappe.db.sql(
        f"""
        SELECT
            priority,
            COUNT(*) AS total_cases,
            SUM(CASE WHEN first_responded_at IS NOT NULL AND first_responded_at <= first_response_due THEN 1 ELSE 0 END) AS responded_on_time,
            SUM(CASE WHEN status IN ('Resolved', 'Closed') AND sla_breached = 0 THEN 1 ELSE 0 END) AS resolved_on_time,
            SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) AS breached,
            AVG(CASE WHEN response_time_hours > 0 THEN response_time_hours END) AS avg_response_hours
        FROM `tabCruelty Report`
        WHERE 1=1 {conditions}
        GROUP BY priority
        ORDER BY FIELD(priority, 'Critical', 'High', 'Medium', 'Low')
        """,
        values,
        as_dict=True,
    )

    return columns, data
