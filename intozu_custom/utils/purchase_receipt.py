from intozu_custom.utils.qr_code import get_qr_code
from erpnext.buying.doctype.purchase_order.purchase_order import set_missing_values
import frappe
import time
from frappe.model.mapper import get_mapped_doc

from frappe.utils.data import flt


@frappe.whitelist()
def qrcode_generate(doc,method):
	for item in doc.items:

		batch = frappe.db.sql("""select name from `tabBatch` where reference_name ="{0}" and item ="{1}" and supplier = "{2}" """.format(doc.name,item.item_code,doc.supplier),as_dict = True)
		serial_no = frappe.db.sql("""select name from `tabSerial No` where purchase_document_no ="{0}" and item_code="{1}" and supplier = "{2}" """.format(doc.name, item.item_code,doc.supplier),as_dict = True)

		for serial in serial_no:
			if batch:
				qr_data = "Product Name : " + item.item_name + " Model No : " + item.item_code +" Batch : "+ batch.name +" S/N : "+ serial.name +" Supplier Code : "+ doc.supplier +" Date : "+ doc.posting_date

				batch=batch[0]
				doc.append("qr_items", {
						'item_code': item.item_code,
						'serial_no': serial['name'],
						'batch_no': batch['name'],
						'qr_code': get_qr_code(qr_data)
				})
			else:
				qr_data = "Product Name : " + item.item_name + " Model No : " + item.item_code +" S/N : "+ serial.name +" Supplier Code : "+ doc.supplier +" Date : "+ doc.posting_date
				doc.append("qr_items", {
						'item_code': item.item_code,
						'serial_no': serial['name'],
						'batch_no':"",
						'qr_code': get_qr_code(qr_data)
				})

            



@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		gbs_doc = frappe.get_doc('Global Buying Settings', "Global Buying Settings")
		if gbs_doc.update_pr_with_zero_qty == 1:
			
				target.qty = 0
			
		else:
			if source_parent.create_pr_with_zero_qty == 1:
				target.qty = 0
			else:
				target.qty = flt(obj.qty) - flt(obj.received_qty)

		target.stock_qty = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.conversion_factor)
		target.amount = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate)
		target.base_amount = (
			(flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate) * flt(source_parent.conversion_rate)
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
		return barcode_data
	elif serial_no_data:
		return serial_no_data
	elif batch_no_data:
		return batch_no_data
	else:
		
		scan_value = dict(search_value)
		frappe.msgprint("search_value is {0}".format(str(scan_value)))
	
	return {}