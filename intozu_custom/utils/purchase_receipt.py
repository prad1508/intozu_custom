import ast
from intozu_custom.utils.qr_code import get_qr_code
from erpnext.buying.doctype.purchase_order.purchase_order import set_missing_values
import frappe
import time
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability
from frappe.utils.data import flt


@frappe.whitelist()
def qrcode_generate(doc, method):

    for item in doc.items:

        batch_no = frappe.db.sql("""select name from `tabBatch` where reference_name ="{0}" and item ="{1}" and supplier = "{2}" """.format(
            doc.name, item.item_code, doc.supplier))
        # batch_no = batch[0][0]
        serial_no = frappe.db.sql("""select name from `tabSerial No` where purchase_document_no ="{0}" and item_code="{1}" and supplier = "{2}" """.format(
            doc.name, item.item_code, doc.supplier), as_dict=True)
        barcode_data = frappe.db.get_value(
            "Item Barcode", {"parent": item.item_code}, ["barcode"])

        for serial in serial_no:
            if batch_no:
                qr_data = {'barcode': barcode_data, 'item_code': item.item_code, 'item_name': item.item_name,
                           'serial_no': serial.name, 'batch': batch_no, 'supplier_code': doc.supplier, 'date': doc.posting_date}
                doc.append("qr_items", {
                    'item_code': item.item_code,
                    'serial_no': serial.name,
                    'batch_no': batch_no,
                    'qr_code': get_qr_code(qr_data)
                })
            else:
                qr_data = {'barcode': barcode_data, 'item_code': item.item_code, 'item_name': item.item_name,
                           'serial_no': serial.name, 'supplier_code': doc.supplier, 'date': doc.posting_date}
                doc.append("qr_items", {
                    'item_code': item.item_code,
                    'serial_no': serial['name'],
                    'batch_no': "",
                    'qr_code': get_qr_code(qr_data)
                })


@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
    def update_item(obj, target, source_parent):
        gbs_doc = frappe.get_doc(
            'Global Buying Settings', "Global Buying Settings")
        if gbs_doc.update_pr_with_zero_qty == 1:

            target.qty = 0

        else:
            if source_parent.create_pr_with_zero_qty == 1:
                target.qty = 0
            else:
                target.qty = flt(obj.qty) - flt(obj.received_qty)

        target.stock_qty = (flt(obj.qty) - flt(obj.received_qty)
                            ) * flt(obj.conversion_factor)
        target.amount = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate)
        target.base_amount = (
            (flt(obj.qty) - flt(obj.received_qty)) *
            flt(obj.rate) * flt(source_parent.conversion_rate)
        )

    doc = get_mapped_doc(
        "Purchase Order",
        source_name,
        {
            "Purchase Order": {
                "doctype": "Purchase Receipt",
                "field_map": {"supplier_warehouse": "supplier_warehouse"},
                "validation": {
                    "docstatus": ["=", 1],
                },
            },
            "Purchase Order Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    "name": "purchase_order_item",
                    "parent": "purchase_order",
                    "bom": "bom",
                    "material_request": "material_request",
                    "material_request_item": "material_request_item",
                },
                "postprocess": update_item,
                "condition": lambda doc: abs(doc.received_qty) < abs(doc.qty)
                and doc.delivered_by_supplier != 1,
            },
            "Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
        },
        target_doc,
        set_missing_values,
    )

    doc.set_onload("ignore_price_list", True)

    return doc


@frappe.whitelist()
def search_for_serial_or_batch_or_barcode_number(search_value):
    # search barcode no
    barcode_data = frappe.db.get_value(
        "Item Barcode", {"barcode": search_value}, ["barcode", "parent as item_code"], as_dict=True
    )
    # search serial no
    serial_no_data = frappe.db.get_value(
        "Serial No", search_value, ["name as serial_no", "item_code"], as_dict=True
    )
    # search batch no
    batch_no_data = frappe.db.get_value(
        "Batch", search_value, ["name as batch_no", "item as item_code"], as_dict=True
    )

    if barcode_data:
        frappe.msgprint("search is {0}".format(barcode_data))
        return barcode_data
    elif serial_no_data:
        return serial_no_data
    elif batch_no_data:
        return batch_no_data
    else:
        string = str(search_value)
        dictionary = ast.literal_eval(string)

        return dictionary

    return {}


@frappe.whitelist()
def search_for_serial_or_batch_or_barcode_number_popup(search_value):
    # search barcode no
    barcode_data = frappe.db.get_value(
        "Item Barcode", {"barcode": search_value}, ["barcode", "parent as item_code"], as_dict=True
    )
    # search serial no
    serial_no_data = frappe.db.get_value(
        "Serial No", search_value, ["name as serial_no", "item_code"], as_dict=True
    )
    # search batch no
    batch_no_data = frappe.db.get_value(
        "Batch", search_value, ["name as batch_no", "item as item_code"], as_dict=True
    )

    if barcode_data:
        return barcode_data
    elif serial_no_data:
        return serial_no_data
    elif batch_no_data:
        return batch_no_data
    else:
        string = str(search_value)
        dictionary = ast.literal_eval(string)
        if dictionary:
            return dictionary

    return {}


def search_by_term(search_term, warehouse, price_list):
    result = search_for_serial_or_batch_or_barcode_number_popup(search_term) or {
    }

    item_code = result.get("item_code") or search_term
    serial_no = result.get("serial_no") or ""
    batch_no = result.get("batch_no") or ""
    barcode = result.get("barcode") or ""

    if result:
        item_info = frappe.db.get_value(
            "Item",
            item_code,
            [
                "name as item_code",
                "item_name",
                "description",
                "stock_uom",
                "image as item_image",
                "is_stock_item",
            ],
            as_dict=1,
        )

        item_stock_qty, is_stock_item = get_stock_availability(
            item_code, warehouse)
        price_list_rate, currency = frappe.db.get_value(
            "Item Price",
            {"price_list": price_list, "item_code": item_code},
            ["price_list_rate", "currency"],
        ) or [None, None]

        item_info.update(
            {
                "serial_no": serial_no,
                "batch_no": batch_no,
                "barcode": barcode,
                "price_list_rate": price_list_rate,
                "currency": currency,
                "actual_qty": item_stock_qty,
            }
        )

        # return {"items": [item_info]}
        return item_info


@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.stock_entry_type = "Material Transfer"
        target.purpose = "Material Transfer"
        target.set_missing_values()

    doclist = get_mapped_doc(
        "Purchase Receipt",
        source_name,
        {
            "Purchase Receipt": {
                "doctype": "Stock Entry",
            },
            "Purchase Receipt Item": {
                "doctype": "Stock Entry Detail",
                "field_map": {
                    "warehouse": "s_warehouse",
                    "parent": "reference_purchase_receipt",
                    "batch_no": "batch_no",
                    "stock_received_qty": "qty",
                    "stock_received_qty": "received_qty",
                },
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist


# update pending_to_receipt QTY in Purchase Order
@frappe.whitelist()
def update_pendding_qty_on_po(self, method):
    on_update_pr_confirm_status(self)
    for item in self.items:
        if item.purchase_order:
            item_code_wise_qty_se = frappe.db.sql("""select sum(qty) from `tabPurchase Receipt Item` where purchase_order ="{0}" and item_code="{1}" """.format(
                item.purchase_order, item.item_code))[0][0]

            item_code_wise_qty = frappe.db.sql(
                """select qty from `tabPurchase Order Item` where parent ="{0}" and item_code="{1}" """.format(item.purchase_order, item.item_code))[0][0]

            pending_qty = flt(item_code_wise_qty) - flt(item_code_wise_qty_se)

            frappe.db.sql("""update `tabPurchase Order Item` set pending_to_receipt ="{0}" where parent="{1}" and item_code="{2}" """.format(
                abs(pending_qty), item.purchase_order, item.item_code))
            frappe.db.commit()


@frappe.whitelist()
def on_update_pr_confirm_status(self):
    for item in self.items:
        if item.purchase_order:
            frappe.db.set_value("Purchase Order", item.purchase_order,
                                'intozi_status', 'Confirmed For Submitted')
