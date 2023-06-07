frappe.ui.form.on('Purchase Receipt', {
    refresh: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (cur_frm.doc.use_qr_in_print === 1) {
            cur_frm.set_df_property('use_qr_in_print', 'read_only', 1);
        }
        if (cur_frm.doc.docstatus === 1) {
            cur_frm.set_df_property('use_qr_in_print', 'hidden', 0);
        }
    },
    // on_submit: function (frm) {
    //     console.log("TEST>>>>>>>>>>>>>>>>>>>.")
    //     frappe.call({
    //         method: "intozu_custom.utils.purchase_receipt.qrcode_generate",
    //         args: {
    //             "name": frm.doc.name
    //         },
    //         callback: function (r) {
    //             if (r.message) {
    //                 frm.set_value("qr_items", r.message)
    //                 frm.refresh_fields("qr_items")
    //                 frm.save("Update")
    //             }
    //         }
    //     })
    // }

});

frappe.ui.form.on('Purchase Receipt', {
    on_submit: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (cur_frm.doc.docstatus === 1) {
            cur_frm.set_df_property('use_qr_in_print', 'hidden', 0);
        }
    }

});

frappe.ui.form.on('Purchase Receipt Item', {
    qty: function (frm, cdt, cdn) {
        var item_row = locals[cdt][cdn];
        cur_frm.fields_dict["items"].$wrapper.find('.grid-body .rows').find(".grid-row").each(function (i, item) {
            let d = locals[cur_frm.fields_dict["items"].grid.doctype][$(item).attr('data-name')];
            if (d["item_code"] == item_row.item_code) {
                $(item).find('.grid-static-col').css({ 'background-color': '#B2FF66' });
                // frappe.utils.scroll_to(
                //         cur_frm.get_field($(item).find('.grid-static-col')).$wrapper,
                //         true,
                //         30
                //     );
                // cur_frm.scroll_to_field('item_code');
                // $(item).wrapper.find('.grid-static-col .grid-row-check:checked:first').prop('checked', 0);
                // man_map.set(item_row.item_code,item_row.idx) ; 
            }
            else {
                $(item).find('.grid-static-col').css({ 'background-color': 'transparent' });
            }
        });
    }
});

frappe.ui.form.on("Purchase Receipt Item", {
    item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn]
        frappe.call({
            method: 'barcode.custom_purchase_receipt.barcode',
            args: {
                item_code: row.item_code,
            },
            callback: (r) => {
                row.item_barcode = r.message
                frm.refresh_fields("items")
            }
        });
    },
    uom: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn]
        frappe.call({
            method: 'barcode.custom_purchase_receipt.barcode_uom',
            args: {
                item_code: row.item_code,
                uom: row.uom
            },
            callback: (r) => {
                row.item_barcode = r.message
                frm.refresh_fields("items")
            }
        });
    }
})