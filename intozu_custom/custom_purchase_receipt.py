import frappe
@frappe.whitelist()
def barcode(item_code):
    doc=frappe.get_doc("Item",item_code)
    barcodes=frappe.db.sql("""select barcode from `tabItem Barcode`  where parent='{0}'  and  uom='{1}' """.format(item_code,doc.stock_uom),as_dict=1)
    if barcodes:
        return barcodes[0].barcode
    else:
        barcodes=frappe.db.sql("""select barcode from `tabItem Barcode`  where parent='{0}'  and  uom is NULL """.format(item_code),as_dict=1)
        if barcodes:
            return barcodes[0].barcode



@frappe.whitelist()
def barcode_uom(item_code,uom):
    doc=frappe.get_doc("Item",item_code)
    barcodes=frappe.db.sql("""select barcode from `tabItem Barcode`  where parent='{0}'  and  uom='{1}' """.format(item_code,uom),as_dict=1)
    if barcodes:
        return barcodes[0].barcode
    else:
        barcodes=frappe.db.sql("""select barcode from `tabItem Barcode`  where parent='{0}'  and  uom is NULL """.format(item_code),as_dict=1)
        if barcodes:
            return barcodes[0].barcode



# @frappe.whitelist()
# def scan_warehouse_barcode(sc):
#     doc=frappe.db.get_value("Warehouse",{"barcode_no":sc},["name"])
#     if doc:
#         return doc
#     else:
#         frappe.throw("No warhouse found for given barcode!!")
