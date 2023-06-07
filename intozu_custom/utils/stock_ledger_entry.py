import frappe
from frappe.utils.data import flt
import time

@frappe.whitelist()
def get_data_in_wle(self,method):
    wle_doc = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':self.warehouse,'item_code':self.item_code}, ['name'])
    if wle_doc:
        current_stock = frappe.db.get_value('Bin', {'warehouse':self.warehouse,'item_code': self.item_code}, ['actual_qty'])
        balance = flt(current_stock) + flt(self.actual_qty)
        if current_stock is not 0.0:
            avail_tot = frappe.get_last_doc('Warehouse Ledger Entry', filters={
                                    'warehouse': self.warehouse, 'item_code': self.item_code})
        # avail_tot = frappe.db.sql("""select available_qty from `tabWarehouse Ledger Entry` where warehouse="{0}" and item_code ="{1}" ORDER BY creation DESC LIMIT 1 """.format(self.warehouse, self.item_code))[0][0]
        # frappe.msgprint("avail_tot {0}".format(avail_tot.name))
        wle = frappe.new_doc("Warehouse Ledger Entry")
        wle.item_code = self.item_code
        wle.warehouse = self.warehouse
        wle.posting_date = self.posting_date
        wle.posting_time = self.posting_time
        
        wle.voucher_type = self.voucher_type
        wle.voucher_no = self.voucher_no
        wle.voucher_detail_no = self.voucher_detail_no
        wle.dependant_sle_voucher_detail_no = self.dependant_sle_voucher_detail_no
        wle.recalculate_rate = self.recalculate_rate

        wle.actual_qty = self.actual_qty
        wle.qty_after_transaction = flt(balance)
        wle.incoming_rate = self.incoming_rate
        wle.outgoing_rate = self.outgoing_rate
        # tot_picked_wle = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':self.warehouse,'item_code':self.item_code}, ['sum(picked_qty)'])
        # tot_reverse_wle = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':self.warehouse,'item_code':self.item_code}, ['sum(reverse_pick)'])
        # tot_avail_wle_picked = flt(tot_picked_wle) - flt(tot_reverse_wle)
        # tot_avail_stock_with_picked = flt(balance) - flt(abs(tot_avail_wle_picked))
        if self.actual_qty > 0:
            # if avail_tot:
            last_avail_wle = frappe.db.get_value('Warehouse Ledger Entry', {'name':avail_tot.name}, ['available_qty'])
            # if last_avail_wle:
            wle.available_qty = flt(last_avail_wle) + self.actual_qty
            # else:
            #     wle.available_qty = self.actual_qty
        
        wle.valuation_rate = self.valuation_rate
        wle.stock_value = self.stock_value
        wle.stock_value_difference = self.stock_value_difference
        wle.stock_queue = self.stock_queue

        wle.company = self.company
        wle.stock_uom = self.stock_uom
        wle.project = self.project
        wle.batch_no = self.batch_no

        wle.fiscal_year = self.fiscal_year
        wle.serial_no = self.serial_no
        wle.is_cancelled = self.is_cancelled
        wle.to_rename = self.to_rename

        wle.ignore_permissions = True
        wle.save()
    else:
        current_stock = frappe.db.get_value('Bin', {'warehouse':self.warehouse,'item_code': self.item_code}, ['actual_qty'])
        balance = flt(current_stock) + flt(self.actual_qty)
        # if current_stock is not 0.0:
        #     avail_tot = frappe.get_last_doc('Warehouse Ledger Entry', filters={
        #                             'warehouse': self.warehouse, 'item_code': self.item_code})
        # avail_tot = frappe.db.sql("""select available_qty from `tabWarehouse Ledger Entry` where warehouse="{0}" and item_code ="{1}" ORDER BY creation DESC LIMIT 1 """.format(self.warehouse, self.item_code))[0][0]
        # frappe.msgprint("avail_tot {0}".format(avail_tot.name))
        wle = frappe.new_doc("Warehouse Ledger Entry")
        wle.item_code = self.item_code
        wle.warehouse = self.warehouse
        wle.posting_date = self.posting_date
        wle.posting_time = self.posting_time
        
        wle.voucher_type = self.voucher_type
        wle.voucher_no = self.voucher_no
        wle.voucher_detail_no = self.voucher_detail_no
        wle.dependant_sle_voucher_detail_no = self.dependant_sle_voucher_detail_no
        wle.recalculate_rate = self.recalculate_rate

        wle.actual_qty = self.actual_qty
        wle.qty_after_transaction = flt(balance)
        wle.incoming_rate = self.incoming_rate
        wle.outgoing_rate = self.outgoing_rate
        # tot_picked_wle = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':self.warehouse,'item_code':self.item_code}, ['sum(picked_qty)'])
        # tot_reverse_wle = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':self.warehouse,'item_code':self.item_code}, ['sum(reverse_pick)'])
        # tot_avail_wle_picked = flt(tot_picked_wle) - flt(tot_reverse_wle)
        # tot_avail_stock_with_picked = flt(balance) - flt(abs(tot_avail_wle_picked))
        if self.actual_qty > 0:
            # if avail_tot:
            #     last_avail_wle = frappe.db.get_value('Warehouse Ledger Entry', {'name':avail_tot.name}, ['available_qty'])
            #     if last_avail_wle:
            #         wle.available_qty = flt(last_avail_wle) + self.actual_qty
            # else:
            wle.available_qty = self.actual_qty
        
        wle.valuation_rate = self.valuation_rate
        wle.stock_value = self.stock_value
        wle.stock_value_difference = self.stock_value_difference
        wle.stock_queue = self.stock_queue

        wle.company = self.company
        wle.stock_uom = self.stock_uom
        wle.project = self.project
        wle.batch_no = self.batch_no

        wle.fiscal_year = self.fiscal_year
        wle.serial_no = self.serial_no
        wle.is_cancelled = self.is_cancelled
        wle.to_rename = self.to_rename

        wle.ignore_permissions = True
        wle.save()