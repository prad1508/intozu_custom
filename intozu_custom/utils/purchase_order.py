import frappe

@frappe.whitelist()
def on_update_pr_change_status(self,method):
    if self.docstatus != 2:
        # if self.short_close != 1:
        for item in self.items:
            if item.purchase_order:
                pending_to_receipt = frappe.db.sql("""select pending_to_receipt from `tabPurchase Order Item` where parent ="{0}" and item_code="{1}" """.format(item.purchase_order, item.item_code))[0][0]

                if pending_to_receipt == 0:
                    frappe.db.set_value("Purchase Order", item.purchase_order, 'intozi_status', 'Completely Receipt')
                
                else:
                    frappe.db.set_value("Purchase Order", item.purchase_order, 'intozi_status', 'Partially Receipt')       
    
        # else:
        #     frappe.db.set_value("Purchase Order", item.purchase_order, 'intozi_status', 'Short Close')

@frappe.whitelist()
def on_cancel_po_change_status(self,method):
   
    frappe.db.set_value(self.doctype, self.name, 'intozi_status', 'Cancelled')

# #on_cancel_pr_change_status
# @frappe.whitelist()
# def on_cancel_po_change_status(self,method):
#     for item in self.items:
#         if item.pending_to_receipt == item.qty:
#             frappe.db.set_value(self.doctype, self.name, 'intozi_status', 'Cancelled')
#         # else:    
#         #     frappe.db.set_value("Purchase Order", item.purchase_order, 'intozi_status', 'Short Close')
#         #     # frappe.db.set_value(self.doctype, self.name, 'intozi_status', 'Cancelled')
        
@frappe.whitelist()
def on_update_po_change_status(self,method):
    if self.short_close == 1:
        frappe.db.set_value(self.doctype, self.name, 'intozi_status', 'Short Close')