import frappe


def execute(filters=None):
    columns = [
        {"fieldname": "province", "label": "Province", "fieldtype": "Data", "width": 160},
        {"fieldname": "city", "label": "City", "fieldtype": "Data", "width": 160},
        {"fieldname": "suburb", "label": "Suburb", "fieldtype": "Data", "width": 180},
        {"fieldname": "total_cases", "label": "Total Cases", "fieldtype": "Int", "width": 130},
        {"fieldname": "open_cases", "label": "Open Cases", "fieldtype": "Int", "width": 130},
        {"fieldname": "critical", "label": "Critical", "fieldtype": "Int", "width": 100},
    ]

    data = frappe.db.sql(
        """
        SELECT
            COALESCE(province, 'Unknown') AS province,
            COALESCE(city, 'Unknown') AS city,
            COALESCE(suburb, 'Unknown') AS suburb,
            COUNT(*) AS total_cases,
            SUM(CASE WHEN status NOT IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS open_cases,
            SUM(CASE WHEN priority = 'Critical' THEN 1 ELSE 0 END) AS critical
        FROM `tabCruelty Report`
        GROUP BY province, city, suburb
        ORDER BY total_cases DESC
        """,
        as_dict=True,
    )

    return columns, data
