frappe.listview_settings['Cruelty Report'] = {
    get_indicator(doc) {
        const status_colors = {
            'Draft': 'grey',
            'Assigned': 'blue',
            'In Progress': 'orange',
            'Escalated': 'red',
            'Resolved': 'green',
            'Closed': 'darkgrey',
            'Reopened': 'purple',
        };
        if (doc.sla_breached && !['Resolved', 'Closed'].includes(doc.status)) {
            return [__('SLA Breached'), 'red', 'sla_breached,=,1'];
        }
        return [__(doc.status), status_colors[doc.status] || 'grey', 'status,=,' + doc.status];
    },

    onload(listview) {
        listview.page.add_action_item(__('Assign Inspector'), () => {
            const selected = listview.get_checked_items();
            if (!selected.length) {
                frappe.msgprint(__('Please select at least one case.'));
                return;
            }
            const d = new frappe.ui.Dialog({
                title: __('Bulk Assign Inspector'),
                fields: [
                    {
                        fieldname: 'inspector',
                        label: __('Inspector'),
                        fieldtype: 'Link',
                        options: 'User',
                        reqd: 1,
                        filters: { role: 'SPCA Inspector' },
                    },
                ],
                primary_action(values) {
                    d.hide();
                    frappe.call({
                        method: 'spca_crm.doctype.cruelty_report.cruelty_report_list.bulk_assign_inspector',
                        args: {
                            case_names: JSON.stringify(selected.map(s => s.name)),
                            inspector: values.inspector,
                        },
                        callback(r) {
                            frappe.show_alert({ message: __('Cases assigned.'), indicator: 'green' });
                            listview.refresh();
                        },
                    });
                },
                primary_action_label: __('Assign'),
            });
            d.show();
        });
    },
};
