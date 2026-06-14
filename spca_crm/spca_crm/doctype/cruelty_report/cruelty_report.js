frappe.ui.form.on('Cruelty Report', {
    refresh(frm) {
        spca_crm.render_case_header(frm);
        spca_crm.add_quick_actions(frm);
        spca_crm.add_assignment_actions(frm);
        spca_crm.toggle_location_map(frm);
    },

    priority(frm) {
        if (frm.doc.priority === 'Critical' && !frm.doc.is_urgent) {
            frm.set_value('is_urgent', 1);
        }
    },

    status(frm) {
        if (frm.doc.status === 'Assigned' && !frm.doc.assigned_inspector) {
            frappe.msgprint(__('Please assign an inspector.'));
        }
    },

    location(frm) {
        spca_crm.toggle_location_map(frm);
    },

    gps_coordinates(frm) {
        spca_crm.toggle_location_map(frm);
    },
});

spca_crm = {
    render_case_header(frm) {
        if (!frm.doc.name || frm.is_new()) return;
        const sla_class = frm.doc.sla_breached ? 'indicator red' : 'indicator green';
        frm.dashboard.set_headline_alert(
            `<div class="${sla_class}">
                <span>Case Age: <b>${frm.doc.case_age_days || 0} days</b></span> &nbsp;|&nbsp;
                <span>Animals: <b>${frm.doc.animal_count || 0}</b></span> &nbsp;|&nbsp;
                <span>SLA: ${frm.doc.sla_breached ? '<b>Breached</b>' : '<b>On Track</b>'}</span>
            </div>`
        );
    },

    add_assignment_actions(frm) {
        if (frm.is_new()) return;

        // Assign to me
        if (!frm.doc.assigned_inspector || frm.doc.assigned_inspector !== frappe.session.user) {
            frm.add_custom_button(__('Assign to Me'), () => {
                spca_crm.assign_to(frm, frappe.session.user);
            }, __('Assign'));
        }

        // Quick assign to any inspector
        frm.add_custom_button(__('Assign Inspector...'), () => {
            spca_crm.show_assign_dialog(frm);
        }, __('Assign'));

        // Unassign
        if (frm.doc.assigned_inspector) {
            frm.add_custom_button(__('Unassign'), () => {
                spca_crm.assign_to(frm, null);
            }, __('Assign'));
        }
    },

    show_assign_dialog(frm) {
        const d = new frappe.ui.Dialog({
            title: __('Assign Inspector'),
            fields: [
                {
                    fieldname: 'inspector',
                    label: __('Inspector'),
                    fieldtype: 'Link',
                    options: 'User',
                    reqd: 1,
                    get_query: () => {
                        return {
                            query: 'spca_crm.spca_crm.doctype.cruelty_report.cruelty_report.get_inspector_query',
                        };
                    },
                },
                {
                    fieldname: 'status_to_assigned',
                    label: __('Set Status to Assigned'),
                    fieldtype: 'Check',
                    default: 1,
                },
            ],
            primary_action(values) {
                d.hide();
                spca_crm.assign_to(frm, values.inspector, values.status_to_assigned);
            },
            primary_action_label: __('Assign'),
        });
        d.show();
    },

    assign_to(frm, inspector, set_status = true) {
        frappe.call({
            method: 'spca_crm.spca_crm.doctype.cruelty_report.cruelty_report.assign_inspector',
            args: {
                case_name: frm.doc.name,
                inspector: inspector || '',
                set_status: set_status ? 1 : 0,
            },
            callback(r) {
                frm.reload_doc();
                frappe.show_alert({
                    message: inspector ? __('Case assigned.') : __('Case unassigned.'),
                    indicator: 'green',
                });
            },
        });
    },

    add_quick_actions(frm) {
        if (frm.is_new()) return;

        frm.add_custom_button(__('Mark First Response'), () => {
            frappe.call({
                method: 'spca_crm.spca_crm.doctype.cruelty_report.cruelty_report.mark_first_response',
                args: { case_name: frm.doc.name },
                callback() {
                    frm.reload_doc();
                    frappe.show_alert({ message: __('First response recorded.'), indicator: 'green' });
                },
            });
        }, __('Actions'));

        frm.add_custom_button(__('Escalate'), () => {
            frappe.prompt(
                {
                    fieldname: 'reason',
                    label: __('Reason for Escalation'),
                    fieldtype: 'Small Text',
                    reqd: 1,
                },
                (values) => {
                    frappe.call({
                        method: 'spca_crm.spca_crm.doctype.cruelty_report.cruelty_report.escalate_case',
                        args: { case_name: frm.doc.name, reason: values.reason },
                        callback() {
                            frm.reload_doc();
                            frappe.show_alert({ message: __('Case escalated.'), indicator: 'orange' });
                        },
                    });
                },
                __('Escalate Case')
            );
        }, __('Actions'));

        if (frm.doc.gps_coordinates) {
            frm.add_custom_button(__('Open in Google Maps'), () => {
                const [lat, lng] = frm.doc.gps_coordinates.split(',').map(s => s.trim());
                window.open(`https://www.google.com/maps/search/?api=1&query=${lat},${lng}`, '_blank');
            }, __('Location'));
        }
    },

    toggle_location_map(frm) {
        const coords = frm.doc.gps_coordinates;
        if (coords && !/^-?\d+\.?\d*\s*,\s*-?\d+\.?\d*$/.test(coords)) {
            frappe.show_alert({ message: __('GPS Coordinates should be "lat, lng"'), indicator: 'orange' });
        }
    },
};
