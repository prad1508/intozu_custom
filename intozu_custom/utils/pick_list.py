import datetime
import time
from erpnext.accounts.utils import get_fiscal_year
import frappe
from frappe.utils.data import cstr, flt


@frappe.whitelist()
def on_submit_so_change_status(self,method):
    create_warehouse_ledger_entry_onsubmit(self)
    if self.docstatus != 2:
        # if self.short_close != 1:
        for item in self.locations:
            pennding_picked_qty = frappe.db.sql("""select pennding_picked_qty from `tabSales Order Item` where parent ="{0}" and item_code="{1}" """.format(item.sales_order, item.item_code))[0][0]

            if pennding_picked_qty == 0:
                frappe.db.set_value("Sales Order", item.sales_order, 'intozi_status', 'Completely Picked')
            
            else:
                frappe.db.set_value("Sales Order", item.sales_order, 'intozi_status', 'Partially Picked')


@frappe.whitelist()
def create_stock_entry_onsubmit(self,method):
    se = frappe.new_doc("Stock Entry")
    for i in self.locations:
        se.append("items", {
            'item_code': i.item_code,
            'item_name': i.item_name,
            # 'rate': i.rate,
            'qty': i.qty,
            'uom': i.uom,
            'stock_uom': i.stock_uom,
            'conversion_factor': 1,
            'serial_no':i.serial_no,
            'batch_no':i.batch_no,
            's_warehouse' : i.warehouse,
            # 't_warehouse':"Delivery Warehouse - ST",
            
        })
    se.stock_entry_type = "Material Transfer"
    se.company = self.company
    se.to_warehouse = "Delivery Warehouse - ST"
    se.apply_putaway_rule = 0
    se.pick_list = self.name
    se.posting_date = self.date
    se.posting_time = self.time
    se.save(ignore_permissions = True)
    se.submit()
    frappe.msgprint(msg='Stock Entry Created Successfully',
                    title='Message',
                    indicator='green')


def create_warehouse_ledger_entry_onsubmit(self):
    # tot_qty = 0.0
    # total_picked = 0.0
    # for item in self.locations:
    #     tot_qty = tot_qty + item.qty
    
    # for item in self.locations:
    #     total_picked = total_picked + item.picked_qty
    for item in self.locations:
        # wle_doc = frappe.db.get_value('Warehouse Ledger Entry', {'voucher_no':self.name,'voucher_type': self.doctype,'item_code':item.item_code}, ['name'])
        # order_qty = frappe.db.get_value('Sales Order Item', {'parent':item.sales_order,'item_code':item.item_code}, ['qty'])
        # tot_qty_org = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(qty)'])
        # cur_stock = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
        # tot_reserv = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':item.warehouse,'item_code':item.item_code}, ['sum(reserved_qty)'])
        # tot_reverse_pick = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':item.warehouse,'item_code':item.item_code}, ['sum(reverse_pick)'])
        avail_tot = frappe.db.sql("""select available_qty from `tabWarehouse Ledger Entry` where warehouse="{0}" and item_code ="{1}" ORDER BY creation DESC LIMIT 1 """.format(item.warehouse, item.item_code))[0][0]
        # tot_picked = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(picked_qty)'])
        if flt(avail_tot) >= item.qty:
            sales = frappe.new_doc("Warehouse Ledger Entry")
            sales.item_code = item.item_code
            sales.warehouse = item.warehouse
            sales.posting_date = self.date
            sales.posting_time = self.time
            sales.fiscal_year = get_fiscal_year(self.date, company=self.company)[0]
            sales.voucher_type = self.doctype
            sales.voucher_no = self.name
            sales.voucher_detail_no = item.name
            if item.original_qty == item.picked_qty:
                sales.type_of_transaction = "Pick Posting"
            else:
                sales.type_of_transaction = "Partially Pick Posting"
            sales.actual_qty = 0
            sales.qty_after_transaction = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
            sales.stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
            sales.incoming_rate = 0
            sales.company = self.company
            sales.batch_no = item.batch_no
            sales.serial_no = item.serial_no
            sales.docstatus = 1
            sales.qty_on_pick = item.original_qty
            # cur_stock = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
            # tot_picked = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(picked_qty)'])
            # tot_picked = flt(tot_reserv) - flt(tot_reverse_pick)
            # avail_tot = tot_qty
            last_entry = frappe.get_last_doc('Warehouse Ledger Entry', filters={
                                        'warehouse': item.warehouse, 'item_code': item.item_code})
            reserved_qty = frappe.db.get_value('Warehouse Ledger Entry', {'name':last_entry.name}, ['reserved_qty'])
            var_add = reserved_qty - item.qty
            sales.picked_qty = item.qty
            sales.available_qty = flt(avail_tot) + flt(var_add)
            # sales.is_cancelled = 1 if self.docstatus == 2 else 0
            sales.ignore_permissions = True
            sales.save()
            # frappe.msgprint(msg='Warehouse Ledger Entry Created Successfully',
                #                 title='Message',
                #                 indicator='green')
        else:
            remaining_qty = flt(avail_tot) - item.qty
            frappe.throw(
                        ("{0} units of Item {1} is not available.").format(
                            abs(remaining_qty), frappe.get_desk_link("Item", item.item_code)
                        ),
                        title=("Insufficient Available Qty"),
                    )

#update pending_to_receipt QTY in Purchase Order
@frappe.whitelist()
def update_pennding_picked_qty_so(self, method):
    create_warehouse_ledger_entry(self)
    on_update_so_confirm_status(self)

    for item in self.locations:
        item_code_wise_qty_se = frappe.db.sql("""select picked_qty from `tabSales Order Item` where parent ="{0}" and item_code="{1}" """.format(item.sales_order, item.item_code))[0][0]
        # frappe.db.sql("""select sum(picked_qty) from `tabPick List Item` where sales_order ="{0}" and item_code="{1}" """.format(item.sales_order, item.item_code))[0][0]
        
        item_code_wise_qty = frappe.db.sql("""select qty from `tabSales Order Item` where parent ="{0}" and item_code="{1}" """.format(item.sales_order, item.item_code))[0][0]

        pending_qty = flt(item_code_wise_qty) - flt(item_code_wise_qty_se)
        
        frappe.db.sql("""update `tabSales Order Item` set pennding_picked_qty ="{0}" where parent="{1}" and item_code="{2}" """.format(abs(pending_qty), item.sales_order, item.item_code))
        frappe.db.commit()


def on_update_so_confirm_status(self):
    if self.docstatus == 0:
        for item in self.locations:
            frappe.db.set_value("Sales Order", item.sales_order, 'intozi_status', 'Pick List Created')     


@frappe.whitelist()
def create_warehouse_ledger_entry(self):
    # tot_qty = 0.0
    # total_picked = 0.0 
    # for item in self.locations:
    #     tot_qty = tot_qty + item.qty

    # for item in self.locations:
    #     total_picked = total_picked + item.picked_qty

    for item in self.locations:
        
        wle_reserved = frappe.db.get_value('Warehouse Ledger Entry', {'voucher_no':self.name,'voucher_type': self.doctype,'item_code':item.item_code,'warehouse':item.warehouse}, ['reserved_qty'])
        # frappe.msgprint("wle_reserved {0}".format(wle_reserved))
        if not wle_reserved:
            # order_qty = frappe.db.get_value('Sales Order Item', {'parent':item.sales_order,'item_code':item.item_code}, ['qty'])
            # cur_stock = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
            # tot_picked = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(picked_qty)'])
            # tot_qty_org = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(qty)'])
            # tot_reserv = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':item.warehouse,'item_code':item.item_code}, ['sum(reserved_qty)'])
            # tot_reverse_pick = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':item.warehouse,'item_code':item.item_code}, ['sum(reverse_pick)'])
            avail_tot = frappe.db.sql("""select available_qty from `tabWarehouse Ledger Entry` where warehouse="{0}" and item_code ="{1}" ORDER BY creation DESC LIMIT 1 """.format(item.warehouse, item.item_code))[0][0]
            # frappe.msgprint("avail_tot {0}".format(avail_tot))
            # if wle_doc:
            #     frappe.db.set_value("Warehouse Ledger Entry", wle_doc, 'qty_on_pick', tot_qty)
            #     frappe.db.set_value("Warehouse Ledger Entry", wle_doc, 'type_of_transaction', "Pick Draft")
            #     # cur_stock = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
            #     # tot_picked = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(picked_qty)'])
            #     # tot_picked = flt(tot_reserv) - flt(tot_reverse_pick)
            #     # avail_tot = cur_stock - flt(tot_picked)
            #     frappe.db.set_value("Warehouse Ledger Entry", wle_doc, 'reserved_qty', tot_qty)
            #     frappe.db.set_value("Warehouse Ledger Entry", wle_doc, 'available_qty', flt(avail_tot)- tot_qty) #- flt(tot_picked_w))
            # else:
            if flt(avail_tot) >= item.qty:
                sales = frappe.new_doc("Warehouse Ledger Entry")
                sales.item_code = item.item_code
                sales.warehouse = item.warehouse
                sales.posting_date = self.date
                sales.posting_time = self.time
                sales.fiscal_year = get_fiscal_year(self.date, company=self.company)[0]
                sales.voucher_type = self.doctype
                sales.voucher_no = self.name
                sales.voucher_detail_no = item.name
                sales.is_reserved_pick = 1
                sales.type_of_transaction = "Pick Draft"
                sales.actual_qty = 0
                sales.qty_after_transaction = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
                sales.stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
                sales.incoming_rate = 0
                sales.company = self.company
                sales.batch_no = item.batch_no
                sales.serial_no = item.serial_no
                sales.docstatus = 1
                sales.qty_on_pick = item.original_qty
                # cur_stock = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
                # tot_picked = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(picked_qty)'])
                # tot_picked = flt(tot_reserv) - flt(tot_reverse_pick)
                # avail_tot = cur_stock - flt(tot_picked)
                sales.reserved_qty = item.qty
                sales.available_qty = flt(avail_tot) - item.qty
                # sales.is_cancelled = 1 if self.docstatus == 2 else 0
                sales.ignore_permissions = True
                sales.save()
                # frappe.msgprint(msg='Warehouse Ledger Entry Created Successfully',
                #                 title='Message',
                #                 indicator='green')
            else:
                remaining_qty = flt(avail_tot) - item.qty
                frappe.throw(
                        ("{0} units of Item {1} is not available.").format(
                            abs(remaining_qty), frappe.get_desk_link("Item", item.item_code)
                        ),
                        title=("Insufficient Available Qty"),
                    )
        
        else:
            avail_tot = frappe.get_last_doc('Warehouse Ledger Entry', filters={
                                    'warehouse': item.warehouse, 'item_code': item.item_code})
            last_avail_wle = frappe.db.get_value('Warehouse Ledger Entry', {'name':avail_tot.name}, ['available_qty'])
            # qty_after_transaction = frappe.db.get_value('Warehouse Ledger Entry', {'name':avail_tot.name}, ['qty_after_transaction'])
            reserved_qty = frappe.db.get_value('Warehouse Ledger Entry', {'name':avail_tot.name}, ['reserved_qty'])
            wle_doc = frappe.db.get_value('Warehouse Ledger Entry', {'is_reserved_pick':1,'voucher_no':self.name,'voucher_type': self.doctype,'item_code':item.item_code,'warehouse':item.warehouse}, ['name'])
            # frappe.msgprint("avail_tot {0}".format(avail_tot))
            tot_a = flt(last_avail_wle) + flt(reserved_qty)
            if flt(tot_a) >= item.qty:
                frappe.db.set_value("Warehouse Ledger Entry", wle_doc, 'reserved_qty', item.qty)
                frappe.db.set_value("Warehouse Ledger Entry", wle_doc, 'available_qty', flt(tot_a)- item.qty)
            else:
                remaining_qty = flt(tot_a) - item.qty
                frappe.throw(
                        ("{0} units of Item {1} is not available.").format(
                            abs(remaining_qty), frappe.get_desk_link("Item", item.item_code)
                        ),
                        title=("Insufficient Available Qty"),
                    )
                


@frappe.whitelist()
def on_cancel_so_confirm_status(self,method):
    # create_warehouse_ledger_entry_oncancel(self)
    for item in self.locations:
        item_code_wise_qty = frappe.db.sql("""select picked_qty from `tabSales Order Item` where parent ="{0}" and item_code="{1}" """.format(item.sales_order, item.item_code))[0][0]
        if item_code_wise_qty == 0:
            frappe.db.set_value("Sales Order", item.sales_order, 'status', 'Submitted')
            frappe.db.set_value("Sales Order", item.sales_order, 'intozi_status', '')    

        else:
            frappe.db.set_value("Sales Order", item.sales_order, 'intozi_status', 'Partially Picked')


@frappe.whitelist()
def create_warehouse_ledger_entry_oncancel(name):
    wle_name = frappe.db.get_value('Warehouse Ledger Entry', {'voucher_no': name,'is_reverse_pick':1}, ['name'])
    if wle_name:
        frappe.db.set_value("Pick List", name, 'pick_status', 'Reverse Pick List')
        frappe.msgprint(msg='This Pick List is Already Cancelled',
                        title='Message',
                        indicator='red')
    else:
        self = frappe.get_doc('Pick List', name)
        # tot_qty = 0.0
        # # total_picked = 0.0 
        # for item in self.locations:
        #     tot_qty = tot_qty + item.qty

        # for item in self.locations:
        #     total_picked = total_picked + item.picked_qty

        for item in self.locations:
            # wle_doc = frappe.db.get_value('Warehouse Ledger Entry', {'voucher_no':self.name,'voucher_type': self.doctype,'item_code':item.item_code}, ['name'])
            # order_qty = frappe.db.get_value('Sales Order Item', {'parent':item.sales_order,'item_code':item.item_code}, ['qty'])
            # cur_stock = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
            # tot_reserv = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':item.warehouse,'item_code':item.item_code}, ['sum(reserved_qty)'])
            # tot_reverse_pick = frappe.db.get_value('Warehouse Ledger Entry', {'warehouse':item.warehouse,'item_code':item.item_code}, ['sum(reverse_pick)'])
            avail_tot = frappe.db.sql("""select available_qty from `tabWarehouse Ledger Entry` where warehouse="{0}" and item_code ="{1}" ORDER BY creation DESC LIMIT 1 """.format(item.warehouse, item.item_code))[0][0]
            # tot_picked = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(picked_qty)'])
            sales = frappe.new_doc("Warehouse Ledger Entry")
            sales.item_code = item.item_code
            sales.warehouse = item.warehouse
            sales.posting_date = self.date
            sales.posting_time = self.time
            sales.fiscal_year = get_fiscal_year(self.date, company=self.company)[0]
            sales.voucher_type = self.doctype
            sales.voucher_no = self.name
            sales.voucher_detail_no = item.name
            # if order_qty == item.picked_qty:
            sales.type_of_transaction = "Reverse Pick"
            # else:
            #     sales.type_of_transaction = "Partially Pick Posting"
            sales.actual_qty = 0
            sales.qty_after_transaction = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
            sales.stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
            sales.incoming_rate = 0
            sales.company = self.company
            sales.batch_no = item.batch_no
            sales.serial_no = item.serial_no
            sales.docstatus = 1
            sales.qty_on_pick = item.original_qty
            # cur_stock = frappe.db.get_value('Bin', {'warehouse':item.warehouse,'item_code': item.item_code}, ['actual_qty'])
            # tot_picked = frappe.db.get_value('Pick List Item', {'sales_order':item.sales_order,'item_code':item.item_code}, ['sum(picked_qty)'])
            # if order_qty == item.picked_qty:
            #     avail_tot = cur_stock - tot_picked
            # else:
            # tot_picked = flt(tot_reserv) - flt(tot_reverse_pick)
            # avail_tot = cur_stock - flt(tot_picked)
            # variance_qty = order_qty - tot_picked
            # avail_tot = avail_tot_p + variance_qty
            sales.reverse_pick = item.qty
            sales.available_qty = flt(avail_tot) + item.qty
            sales.is_reverse_pick = 1
            sales.ignore_permissions = True
            sales.save()
            frappe.msgprint(msg='Pick List is Cancelled Successfully',
                        title='Message',
                        indicator='red')
        
        frappe.db.set_value("Pick List", self.name, 'pick_status', 'Reverse Pick List')


# @frappe.whitelist()
# def validation_on_pick_list(self,method):
#     for item in self.locations:
#         avail_tot = frappe.get_last_doc('Warehouse Ledger Entry', filters={
#                                 'warehouse': item.warehouse, 'item_code': item.item_code})
        
#         last_avail_wle = frappe.db.get_value('Warehouse Ledger Entry', {'name':avail_tot.name}, ['available_qty'])

#         if item.qty > last_avail_wle:
#             frappe.msgprint(msg='Available Qty is not enough. Qty is more then Available Qty',
#                         title='Message',
#                         indicator='red')

#             return            