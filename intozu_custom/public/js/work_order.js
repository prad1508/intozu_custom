frappe.ui.form.on('Work Order', {
    refresh: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (cur_frm.doc.use_qr_in_print === 1) {
            cur_frm.set_df_property('use_qr_in_print', 'read_only', 1);
        }
        if (cur_frm.doc.docstatus === 1) {
            cur_frm.set_df_property('use_qr_in_print', 'hidden', 0);
        }
    }

});

frappe.ui.form.on('Work Order', {
    on_submit: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (cur_frm.doc.docstatus === 1) {
            cur_frm.set_df_property('use_qr_in_print', 'hidden', 0);
            frappe.model.set_value(d.doctype, d.name, 'use_qr_in_print', 0);
        }
    }

});

frappe.ui.form.on('Work Order', {
    use_qr_in_print: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (d.use_qr_in_print === 1) {
            msgprint('Please Make Sure Your Manufacture Stock Entry Is Submitted');
        }
    }

});


frappe.ui.form.on('Work Order', {
    onload: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (frm.doc.__islocal) {
            frappe.call({
                method: "intozu_custom.utils.work_order.company_address",
                args: {
                    name: d.company,
                },
                callback: function (r) {
                    // console.log(r.message[0])
                    frappe.call({
                        method: 'frappe.client.get_value',
                        args: {
                            'doctype': 'Address',
                            'filters': { 'name': r.message[0] },
                            'fieldname': [
                                'address_line1', 'address_line2', 'city', 'state', 'country', 'pincode'
                            ]
                        },
                        callback: function (s) {
                            // console.log(s.message)
                            var addr = s.message.address_line1 + " " + s.message.city + " " + s.message.state + " " + s.message.country + "-" + s.message.pincode
                            // console.log(addr)
                            frappe.model.set_value(d.doctype, d.name, "company_address_name", addr)
                        }
                    })
                }
            })
        }
    }
})

frappe.ui.form.on("Work Order", {
    production_item: function (frm) {
        frappe.call({
            method: 'barcode.custom_work_order.barcode',
            args: {
                item_code: frm.doc.production_item,
            },
            callback: (r) => {
                // console.log("******************************",r.message)
                frm.doc.barcode = r.message
                frm.set_value("barcode", r.message)
                frm.refresh_fields("barcode")
            }
        });
    },
    before_save: function (frm) {
        frappe.call({
            method: 'barcode.custom_work_order.barcode',
            args: {
                item_code: frm.doc.production_item,
            },
            callback: (r) => {
                // console.log("******************************",r.message)
                frm.doc.barcode = r.message
                frm.set_value("barcode", r.message)
                frm.refresh_fields("barcode")
            }
        });
    }
})