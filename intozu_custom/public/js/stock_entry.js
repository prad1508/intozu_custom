// Create Pop-up For Barcode and QR code Scanning...
frappe.ui.form.on('Stock Entry', {
    refresh: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        frappe.model.set_value(d.doctype, d.name, 'apply_putaway_rule', 1);
        frm.add_custom_button(__("Scan Items"), function () {
            frm.trigger("scan_item");
        });
    },
    scan_item: function (frm) {
        var data = [];
        //Create Dialog Popup for Scan Barcode and QR Code
        const dialog = frappe.prompt([
            {
                fieldtype: 'Link',
                options: 'Warehouse',
                fieldname: 'warehouse',
                label: __('Warehouse')

            },
            {
                fieldtype: 'Data',
                fieldname: 't_qty_receipt',
                label: __('Total Qty Receipt')

            },
            {
                fieldtype: 'Data',
                fieldname: 'scan_qty',
                label: __('Scan Qty')

            },{
                fieldtype: 'Data',
                fieldname: 'r_qty',
                label: __('Remaining Qty')

            },
            { fieldtype: "Column Break" },
            {
                fieldtype: 'Small Text',
                options: 'Barcode',
                height: 140,
                fieldname: 'barcode_scan',
                label: __('Barcode Scan'),
                onchange: function (e) {
                    barcode_item(e)
                }

            },
            { fieldtype: "Section Break" },
            {

                fieldname: 'scan_child',
                fieldtype: 'Table',
                label: (__("Scan Details")),
                data: data,
                get_data: function () {
                    return data
                },
                fields: [
                    {
                        fieldtype: 'Link',
                        options: 'Item',
                        fieldname: 'item_code',
                        label: __('Item Code'),
                        in_list_view: 1
                    },
                    {
                        fieldtype: 'Float',
                        fieldname: 'received_qty',
                        label: __('Received Qty'),
                        in_list_view: 1

                    },
                    {
                        fieldtype: 'Link',
                        options: 'Warehouse',
                        fieldname: 'target_warehouse',
                        label: __('Target Warehouse'),
                        in_list_view: 1

                    },
                    {
                        fieldtype: 'Link',
                        options: 'Batch',
                        fieldname: 'batch',
                        label: __('Batch No'),
                        in_list_view: 1

                    },
                    {
                        fieldtype: 'Link',
                        options: 'Serial No',
                        fieldname: 'serial_no',
                        label: __('Serial No'),
                        in_list_view: 1

                    },
                ],

            },
        ],
            function (r) {

                add_items(dialog);

            });

            // Fetch Items From Barcode and QR Code Response
            function barcode_item(e) {

                if (cur_dialog.fields_dict.barcode_scan.value) {
                    frappe.call({
                        method: "intozu_custom.utils.purchase_receipt.search_for_serial_or_batch_or_barcode_number_popup",
                        args: {
                            search_value: cur_dialog.fields_dict.barcode_scan.value
                        },
                        callback: function (r) {
                            if (r.message) {

                                data.push({
                                    'item_code': r.message.item_code,
                                    'batch': r.message.batch,
                                    'received_qty': 1,
                                    'target_warehouse': cur_dialog.fields_dict.warehouse.value,
                                    'serial_no': r.message.serial_no,

                                });
                                cur_dialog.fields_dict.scan_child.grid.refresh();
                                cur_dialog.fields_dict.barcode_scan.set_value('');
                            }
                        }
                    });
                }

            };

    }
});

// Fetch Items from Dialog box to main Doc Items Table
function add_items(dialog) {
    let cur_grid = cur_frm.fields_dict.items.grid;
    console.log(cur_grid)
    var scan_item = dialog.fields_dict.scan_child.df.data;

    for (let item of scan_item) {
        const existing_item_row = cur_frm.doc.items.find(d => d.item_code === item.item_code && d.t_warehouse == item.target_warehouse);
        const blank_item_row = cur_frm.doc.items.find(d => !d.item_code);

        if (existing_item_row) {

            frappe.model.set_value(existing_item_row.doctype, existing_item_row.name, {
                item_code: item.item_code,
                received_qty: (existing_item_row.received_qty || 0) + 1
            });
        } else if (blank_item_row) {
            console.log(blank_item_row);

            let row = frappe.model.add_child(cur_frm.doc, 'Stock Entry Detail', 'items');
            row.item_code = item.item_code;
            row.received_qty = + 1;
            row.qty = + 1;
            row.conversion_factor = 1;
            row.serial_no = item.serial_no;
            row.t_warehouse = item.target_warehouse;
            row.batch_no = item.batch;
            frappe.db.get_doc('Item', null, { name: item.item_code })
                .then(doc => {
                    row.uom = doc.stock_uom;
                });

            refresh_field('items');
        }
    }
}

// Set Qty value Same as a Received Qty value on Save
frappe.ui.form.on('Stock Entry', {
    before_save: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        for (let item of d.items) {
            console.log(item)
            frappe.model.set_value(item.doctype, item.name, "qty", item.received_qty);
        }
    }
})
