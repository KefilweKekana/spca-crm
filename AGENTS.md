# Agent Notes: SPCA Helpdesk

## App Layout

- `spca_crm/spca_crm/doctype/` — DocType definitions (JSON) and controllers (Python).
- `spca_crm/spca_crm/report/` — Script reports.
- `spca_crm/spca_crm/fixtures/` — Static fixtures loaded on install/migrate.
- `spca_crm/spca_crm/client_scripts/` — Custom JS for foreign DocTypes (e.g. Cruelty_Form).
- `spca_crm/spca_crm/setup/install.py` — Bootstraps roles, default branch, settings and fixtures.
- `spca_crm/spca_crm/utils.py` — Shared helpers and web-form conversion.
- `spca_crm/spca_crm/webform_hooks.py` — Hook for configured public web form DocType.

## Coding Conventions

- Use `frappe.get_doc` and `frappe.db.sql` as per Frappe patterns.
- Keep business logic in DocType controller methods, not client scripts.
- Child table rows are `Document` instances; iterate with `doc.get("table_field", [])`.
- SLA times are calculated in `CrueltyReport.set_sla_due_dates()` based on priority.
- Use `frappe.log_error` for scheduled-task failures so they don't break the scheduler.
- Web form conversion is permission-gated via `SPCA CRM Settings.role_allowed_to_convert`.

## Web Form Integration

The public webform DocType is configured in **SPCA CRM Settings** (`web_form_doctype`, default `Cruelty_Form`).

- `webform_hooks.on_cruelty_form_after_insert` runs on `after_insert` of that DocType.
- `utils.create_cruelty_report_from_webform()` maps fields dynamically using `Web Form Field Mapping`.
- Default field mappings are provided for common field names; override in settings.
- Manual conversion button is added to `Cruelty_Form` via `client_scripts/cruelty_form.js`.

## Testing

Unit tests live in `spca_crm/spca_crm/tests/`. Run with:

```bash
bench --site your-site run-tests --app spca_crm
```

## Fixtures

When modifying fixtures, update both the JSON file in `fixtures/` and the `load_fixtures()` registry in `setup/install.py`. The `fixtures` list in `hooks.py` is only for export from a running site.

## Version Compatibility

- Target Frappe/ERPNext v15 and v16.
- Avoid APIs deprecated in v15; use `frappe.utils.time_diff_in_hours` for time math.
- Keep Python version `>=3.10`.

## Common Tasks

### Add a new status
1. Update `Cruelty Report` status options.
2. Update `workflow_cruelty_report.json` states/transitions.
3. Update `hooks.py` Workflow State filter list.
4. Update list view indicator in `cruelty_report_list.js`.

### Change SLA targets
Edit `CrueltyReport.set_sla_due_dates()` in `cruelty_report.py`.

### Connect a different public web form DocType
1. Go to **SPCA CRM Settings** and change `web_form_doctype`.
2. Update the field mapping table.
3. Ensure the DocType's `after_insert` hook is wired in `hooks.py`.
