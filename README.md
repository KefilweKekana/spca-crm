# SPCA Helpdesk

An ERPNext module for SPCA organisations to manage cruelty reports, inspections, and case workflows.

## Features

- **Cruelty Report Management** — capture, assign, track and close cases.
- **SLA Tracking** — automatic response/resolution due dates per priority with breach alerts.
- **Workflow** — Draft → Assigned → In Progress → Escalated → Resolved → Closed.
- **Inspection Visits** — log visits, findings, evidence photos and follow-ups.
- **People & Animals** — manage complainants, suspects, witnesses and animals involved.
- **Dashboard & Reports** — workspace with number cards, charts and script reports.
- **Public Web Form Integration** — auto-convert submissions from your existing webform (`Cruelty_Form`) into cases.
- **Permission Control** — configurable role gate for manual webform conversion.
- **Easy Assignment** — Assign to Me, Quick Assign dialog, bulk assignment, unassign.
- **Print Format** — case file print-out for legal/prosecution use.
- **Scheduled Jobs** — overdue SLA alerts and auto-closure of resolved cases.

## DocTypes

| DocType | Purpose |
|---------|---------|
| Cruelty Report | Main case file |
| Complainant | Person reporting cruelty (re-usable) |
| SPCA Branch | Branch/region configuration |
| SPCA Helpdesk Settings | Web form mapping, defaults and permissions |
| Animal Involved | Child table of animals in a case |
| Case Suspect | Child table of suspects |
| Case Witness | Child table of witnesses |
| Inspection Visit | Child table of on-site visits |
| Case Note | Child table of chronological notes |
| Web Form Field Mapping | Maps web form fields to Cruelty Report fields |

## Roles

- **SPCA Call Operator** — captures reports and complainants.
- **SPCA Inspector** — investigates, logs visits, resolves cases.
- **SPCA Manager** — assigns, escalates, closes and reports.

## Installation

```bash
bench get-app https://github.com/spca/spca_crm.git
bench --site your-site install-app spca_crm
bench --site your-site migrate
```

After install, open **SPCA Helpdesk Settings** and confirm:
- **Web Form DocType** = `Cruelty_Form`
- **Web Form Route** = `report`
- Configure field mapping if your `Cruelty_Form` fields differ from the defaults.

## Web Form Integration

Submissions from your existing `Cruelty_Form` webform are automatically converted into `Cruelty Report` records via the `after_insert` hook.

### Manual conversion
Open any `Cruelty_Form` record and use **SPCA → Convert to SPCA Case**. This action is gated by the role configured in **SPCA Helpdesk Settings** (`role_allowed_to_convert`).

### Permission
Set **Role Allowed to Convert Web Submissions** in SPCA Helpdesk Settings. The automatic conversion bypasses this check (system process), but manual conversion respects it.

## Inspector Assignment

From a Cruelty Report form:
- **Assign → Assign to Me**
- **Assign → Assign Inspector...** (filtered to users with SPCA Inspector role)
- **Assign → Unassign**

From the list view:
- Select multiple cases → **Assign Inspector** action.

## Compatibility

- ERPNext v15+
- ERPNext v16+
- Python 3.10+

## License

MIT
