frappe.ui.form.on('Purchase Receipt', {
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
