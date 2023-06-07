import frappe
from frappe.utils.data import flt


@frappe.whitelist()
def update_pendding_qty(self, method):
    on_update_pr_confirm_status(self)
    for item in self.items:
        if item.reference_purchase_receipt:
            item_code_wise_qty_se = frappe.db.sql("""select sum(qty) from `tabStock Entry Detail` where reference_purchase_receipt ="{0}" and item_code="{1}" """.format(
                item.reference_purchase_receipt, item.item_code))[0][0]
            frappe.db.sql("""update `tabPurchase Receipt Item` set stock_received_qty ="{0}" where parent="{1}" and item_code="{2}" """.format(
                flt(item_code_wise_qty_se), item.reference_purchase_receipt, item.item_code))

            item_code_wise_qty = frappe.db.sql("""select qty from `tabPurchase Receipt Item` where parent ="{0}" and item_code="{1}" """.format(
                item.reference_purchase_receipt, item.item_code))[0][0]

            item_code_wise_srq = frappe.db.sql("""select stock_received_qty from `tabPurchase Receipt Item` where parent ="{0}" and item_code="{1}" """.format(
                item.reference_purchase_receipt, item.item_code))[0][0]
            pending_qty = flt(item_code_wise_qty) - flt(item_code_wise_srq)
            # frappe.msgprint("item_code_wise_qty is {0} pending_qty is {1}".format(item_code_wise_qty, pending_qty))
            frappe.db.sql("""update `tabPurchase Receipt Item` set stock_pending_qty ="{0}" where parent="{1}" and item_code="{2}" """.format(
                abs(pending_qty), item.reference_purchase_receipt, item.item_code))
            frappe.db.commit()


@frappe.whitelist()
def on_update_pr_confirm_status(self):
    for item in self.items:
        if item.reference_purchase_receipt:
            frappe.db.set_value("Purchase Receipt", item.reference_purchase_receipt,
                                'intozi_status', 'Confirmed For Submitted')


@frappe.whitelist()
def on_update_se_change_status(self, method):
    if self.docstatus != 2:
        for item in self.items:
            if item.reference_purchase_receipt:
                stock_pending_qty = frappe.db.sql("""select stock_pending_qty from `tabPurchase Receipt Item` where parent ="{0}" and item_code="{1}" """.format(
                    item.reference_purchase_receipt, item.item_code))[0][0]

                if stock_pending_qty == 0:
                    frappe.db.set_value(
                        "Purchase Receipt", item.reference_purchase_receipt, 'intozi_status', 'Completely Putway')

                else:
                    frappe.db.set_value(
                        "Purchase Receipt", item.reference_purchase_receipt, 'intozi_status', 'Partially Putway')
