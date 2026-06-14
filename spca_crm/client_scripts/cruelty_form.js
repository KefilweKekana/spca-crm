frappe.ui.form.on('Cruelty_Form', {
    refresh(frm) {
        if (frm.doc.docstatus !== 2 && !frm.doc.spca_cruelty_report) {
            frm.add_custom_button(__('Convert to SPCA Case'), () => {
                frappe.call({
                    method: 'spca_crm.spca_crm.utils.convert_webform_to_case',
                    args: {
                        source_doctype: frm.doc.doctype,
                        source_name: frm.doc.name,
                    },
                    freeze: true,
                    freeze_message: __('Converting to Cruelty Report...'),
                    callback(r) {
                        if (r.message && r.message.cruelty_report) {
                            frappe.show_alert({
                                message: __('Converted to ') + r.message.cruelty_report,
                                indicator: 'green',
                            });
                            frm.reload_doc();
                        }
                    },
                });
            }, __('SPCA'));
        }

        if (frm.doc.spca_cruelty_report) {
            frm.add_custom_button(__('Open Cruelty Report'), () => {
                frappe.set_route('Form', 'Cruelty Report', frm.doc.spca_cruelty_report);
            }, __('SPCA'));
        }
    },
});
