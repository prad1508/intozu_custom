from intozu_custom.utils.qr_code import get_qr_code
import frappe

@frappe.whitelist()
def qrcode_generate(doc,method):
    se_name = frappe.db.get_value('Stock Entry', {'work_order': doc.name,'stock_entry_type': "Manufacture"}, ['name'])

    batch = frappe.db.sql("""select name from `tabBatch` where reference_name ="{0}" and item ="{1}" """.format(se_name,doc.production_item),as_dict = True)[0]
    serial_no = frappe.db.sql("""select name from `tabSerial No` where purchase_document_no ="{0}" and item_code="{1}" """.format(se_name, doc.production_item),as_dict = True)

    for serial in serial_no:
        
        if batch:
            qr_data = "Product Name : " + doc.item_name + " Model No : " + doc.production_item +" Batch : "+ batch.name +" S/N : "+ serial.name +" Date : "+ doc.actual_end_date

            doc.append("qr_items", {
                    'item_code': doc.production_item,
                    'serial_no': serial['name'],
                    'batch_no': batch['name'],
                    'qr_code': get_qr_code(qr_data)
            })
        else:
            qr_data = "Product Name : " + doc.item_name + " Model No : " + doc.production_item +" S/N : "+ serial.name +" Date : "+ doc.actual_end_date
            doc.append("qr_items", {
                    'item_code': doc.production_item,
                    'serial_no': serial['name'],
                    'batch_no':"",
                    'qr_code': get_qr_code(qr_data)
            })

        # frappe.msgprint("serial is {0} batch is {1}".format(serial,batch))



@frappe.whitelist()
def company_address(name):

    scrapitems = frappe.db.sql("select parent from `tabDynamic Link` where link_name= %s", name)

    return scrapitems[0]