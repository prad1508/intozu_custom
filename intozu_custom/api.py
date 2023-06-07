import array
import json
import frappe
from frappe import _
from erpnext.accounts.party import get_dashboard_info
from frappe.utils.data import flt, get_time, getdate, today
from frappe.utils import get_site_name
from frappe.utils.data import flt

@frappe.whitelist(allow_guest=True)
def add_lead_doc(lead_name,email_id,mobile_no,source,notes):
    try:
        doc = frappe.new_doc("Lead")
        doc.lead_name = lead_name
        doc.email_id = email_id
        doc.source = source
        doc.mobile_no = mobile_no
        doc.notes = notes
        doc.status = "Lead"
        doc.save(ignore_permissions = True)
        lead = "Lead Source Added Successfully"

        return lead

    except Exception as e:

        return e



@frappe.whitelist()
def add_material_request_doc(material_request_type,company,transaction_date,
item_code,schedule_date,description,qty,stock_uom,uom):
    try:
        doc = frappe.new_doc("Material Request")
        doc.material_request_type = material_request_type
        doc.company = company
        doc.transaction_date = transaction_date
        doc.item_code = item_code
        doc.schedule_date = schedule_date
        doc.description = description
        doc.qty = qty
        doc.stock_uom = stock_uom
        doc.uom = uom
        doc.conversion_factor = 1

        doc.save(ignore_permissions = True)
        lead = "Material Request Added Successfully"

        return lead

    except Exception as e:

        return e


@frappe.whitelist()
def get_sales_order_list(customer_name=None, from_date=None, to_date=None):
    try:
        # Build the filters for the sales orders
        filters = []
        if customer_name:
            filters.append(["Sales Order", "customer_name", "=", customer_name])
        if from_date:
            filters.append(["Sales Order", "transaction_date", ">=", from_date])
        if to_date:
            filters.append(["Sales Order", "transaction_date", "<=", to_date])

        # Retrieve the sales orders from the database
        sales_orders = frappe.get_all("Sales Order", filters=filters, fields=["name", "customer_name", "transaction_date", "status", "grand_total", "total_taxes_and_charges", "address_display"])

        # Convert the sales orders to a list of dictionaries
        sales_orders_list = []
        for sales_order in sales_orders:
            items = frappe.db.get_list("Sales Order Item", {"parent": sales_order.name}, ["item_code", "qty", "rate", "amount", "image"])
            sales_orders_list.append({
                "order_number": sales_order.name,
                "customer_name": sales_order.customer_name,
                "customer_address": sales_order.address_display,
                "order_date": sales_order.transaction_date,
                "order_status": sales_order.status,
                "total_amount": sales_order.grand_total,
                "total_taxes_and_charges": sales_order.total_taxes_and_charges,
                "items" : items
            })

        frappe.response["message"] = {
            "success_key":1,
            "message":"Sales Orders List",
            "response": sales_orders_list
        }


    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }


# @frappe.whitelist()
# def get_vegetable_item_list():
#     try:
        
#         filters = []
        
#         filters.append(["Item", "item_category", "=", "Vegetable"])
        
#         item = frappe.get_all("Item",  filters=filters,fields=["name","image","standard_rate","stock_uom"])

        
#         item_list = []
#         for items in item:
            

#             # Mark a string for translation
#             my_string = items.name

#             # Translate the string to Hindi
#             # print(translate(my_string, language="hi"))
#             item_list.append({
#                 "item": items.name,
#                 "name_hindi":frappe._(str=my_string, language="hi"),
#                 "image": items.image,
#                 "standard_rate":items.standard_rate,
#                 "stock_uom": items.stock_uom
               
#             })

#         frappe.response["message"] = {
#             "success_key":1,
#             "message":"Vegetable Item List",
#             "response": item_list
#         }


    # except frappe.exceptions:
    #     frappe.clear_messages()
    #     frappe.local.response["message"] = {
    #         "success_key":0,
    #         "message":"Data Error!"
    #     }


@frappe.whitelist()
def get_vegetable_item_list():
   try:
        
      filters = []

      filters.append(["Item", "item_category", "=", "Vegetable"])

      item = frappe.get_all("Item",  filters=filters,fields=["name","image","standard_rate","sales_uom"])

   
           
      item_list = []
      for items in item:
         pack=[]
         if items.sales_uom:
            uom=frappe.get_doc("Item Pack",{"uom":items.sales_uom})
            for j in uom.pack_details:
               pack.append({"packId":items.name,"qty":str(j.pack),"uomId":str(items.get("sales_uom")),"uomName":str(items.get("sales_uom"))})

         item_list.append({
               "item": items.name,
               "image": items.image,
               "standard_rate":items.standard_rate,
               "stock_uom": items.sales_uom,
               "pack":pack
            
         })

      return item_list


   except frappe.exceptions:
      frappe.clear_messages()
      frappe.local.response["message"] = {
         "success_key":0,
         "message":"Data Error!"
      }



@frappe.whitelist()
def get_fruits_item_list():
    try:
        filters = []

        filters.append(["Item", "item_category", "=", "Fruits"])

        item = frappe.get_all("Item",  filters=filters,fields=["name","image","standard_rate","sales_uom"])


        item_list = []
        for items in item:
            product=""
            site_name = get_site_name(frappe.local.request.host)

            if item.image:
                product=str(site_name)+str(item.image)
            
            pack=[]
            if items.sales_uom:
                uom=frappe.get_doc("Item Pack",{"uom":items.get("sales_uom")})
            for j in uom.pack_details:
                pack.append({"packId":items.name,"qty":str(j.pack),"uomId":str(items.get("sales_uom")),"uomName":str(items.get("sales_uom"))})
            
            item_list.append({
                "item": items.name,
                "image": product,
                "standard_rate":items.standard_rate,
                "stock_uom": items.sales_uom,
                "pack":pack
            })

        return item_list


    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }


@frappe.whitelist()
def get_fruits_item_list():
    try:
        
        filters = []
        
        filters.append(["Item", "item_category", "=", "Fruits"])
        
        item = frappe.get_all("Item",  filters=filters,fields=["name","image","standard_rate","stock_uom"])

       
        item_list = []
        for items in item:
            
            item_list.append({
                "item": items.name,
                "image": items.image,
                "standard_rate":items.standard_rate,
                "stock_uom": items.stock_uom
            })

        frappe.response["message"] = {
            "success_key":1,
            "message":"Fruits Item List",
            "response": item_list
        }


    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }



@frappe.whitelist()
def update_sales_order(sales_order=None , items=None):
    data = json.loads(items)
    try:
        sales_order = frappe.get_doc("Sales Order", sales_order)
        sales_order.set("items", [])
        for item in data:
            description = frappe.db.get_value('Item', {'name': item["item_code"]}, ['description'])
            stock_uom = frappe.db.get_value('Item', {'name': item["item_code"]}, ['stock_uom'])
            sales_order.append("items", {
                "item_code": item["item_code"],
                "qty": item["qty"],
                "item_name": item["item_name"],
                "description": description,
                "uom": stock_uom,
                "conversion_factor": 1,
                "delivery_date" : sales_order.delivery_date
            })

        sales_order.save(ignore_permissions = True)
        sales_order.reload()
       
        frappe.response["message"] = {
            "success_key":1,
            "message":"Qty has been Updated in Sales Order Item",
            "response": sales_order
        }

    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }



@frappe.whitelist()
def get_oe_assgined_area(territory = None):
    try:
        if territory:
            filters = []
            
            filters.append(["Employee", "territory", "=", territory])
            
            emps = frappe.get_all("Employee",  filters=filters,fields=["first_name","last_name","territory","cell_number"])

        else:
            emps = frappe.get_all("Employee", fields=["first_name","last_name","territory","cell_number"])

        emp_list = []
        for emp in emps:
            emp_list.append({
                "first_name": emp.first_name,
                "last_name": emp.last_name,
                "territory":emp.territory,
                "cell_number": emp.cell_number
            })

        frappe.response["message"] = {
            "success_key":1,
            "message":"OE Assgined Area List",
            "response": emp_list
        }


    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }


@frappe.whitelist()
def get_payment_list(customer = None):
    try:
        if customer:
            filters = []
            
            filters.append(["Payment Entry", "party", "=", customer])
            
            payment_entry = frappe.get_all("Payment Entry",  filters=filters,fields=["name","posting_date","paid_amount","status","mode_of_payment","party","party_name"])

        else:
            payment_entry = frappe.get_all("Payment Entry", fields=["name","posting_date","paid_amount","status","mode_of_payment","party","party_name"])

        pe_list = []
        for pe in payment_entry:
            full_name = frappe.db.get_value('User', {'name': frappe.session.user}, ['full_name'])
            pe_list.append({
                "id": pe.name,
                "date": pe.posting_date,
                "payment": pe.mode_of_payment,
                "paid_amount": pe.paid_amount,
                "status": pe.status,
                "operationExecutiveId" : frappe.session.user,
                "operationExecutiveName" : full_name,
                "collector_type": frappe.session.user,
                "vendor_id": pe.party,
                "vendor_name": pe.party_name
                
            })

        frappe.response["message"] = {
            "success_key":1,
            "message":"Payment Entry List",
            "response": pe_list
        }


    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }        



@frappe.whitelist()
def make_payment_entry(mode_of_payment,amount,party):
    try:
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.mode_of_payment = mode_of_payment
        # pe.paid_from = "ZZ"
        # pe.paid_to = ""
        pe.paid_from_account_currency = "INR"
        pe.paid_to_account_currency = "INR"
        pe.paid_amount = amount
        pe.party_type = "Customer"
        pe.received_amount = amount
        pe.source_exchange_rate = 1
        pe.target_exchange_rate = 1
        pe.base_paid_amount = amount
        pe.base_received_amount = amount
        pe.unallocated_amount = amount
        pe.party = party
        pe.save(ignore_permissions = True)
       
        frappe.response["message"] = {
            "success_key":1,
            "message":"Payment Entry Created Successfully",
            "response": pe
        }


    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }        
    



@frappe.whitelist()
def get_profile_details(user):
    try:
        user_doc = frappe.get_doc("User",user)
        user_list=[]
        site_name = get_site_name(frappe.local.request.host)
        img = frappe.db.get_value('Employee', {'user_id': user_doc.email}, ['image']) or ""
        user_list.append({
            "name":user_doc.full_name,
            "phone":frappe.db.get_value('Employee', {'user_id': user_doc.email}, ['emergency_phone_number']) or "",
            "mobile":frappe.db.get_value('Employee', {'user_id': user_doc.email}, ['cell_number']) or "",
            "current_address":frappe.db.get_value('Employee', {'user_id': user_doc.email}, ['current_address']) or "",
            "vendorCode":frappe.db.get_value('Employee', {'user_id': user_doc.email}, ['name']) or "",
            "vendorGrade":frappe.db.get_value('Employee', {'user_id': user_doc.email}, ['grade']) or "",
            # "balance":user_doc.full_name,
            "area":frappe.db.get_value('Employee', {'user_id': user_doc.email}, ['territory']) or "",
            "defaultBalance":frappe.db.get_value('Employee', {'user_id': user_doc.email}, ['default_balance']) or 0.0,
            "image":str(site_name)+str(img) if img else ""
            
        })

        frappe.response["message"] = {
            "success_key":1,
            "message":"User Details",
            "response": user_list
        }


    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }        




@frappe.whitelist()
def update_item_price(rate,item_code,warehouse,price_list):
    try:
        frappe.db.sql("""update `tabItem Price` set price_list_rate="{0}" where item_code="{1}" and warehouse="{2}" and price_list="{3}" """.format(rate,item_code,warehouse,price_list))
        frappe.db.commit()
        frappe.response["message"] = {
            "success_key":1,
            "message":"Item Price is Updated Successfully"
        }


    except frappe.exceptions:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Data Error!"
        }        




@frappe.whitelist()
def get_sm_sales_order_list(sales_executive=None,date=None):
    try:
        if sales_executive:
            # Build the filters for the sales orders
            customer_list = frappe.db.get_list("Customer", {"sales_executive": sales_executive}, ["name"])
            for customer in customer_list:
                filters = []
                if customer:
                    
                    filters.append(["Sales Order", "customer", "=", customer.name])
                
                if date:
                    filters.append(["Sales Order", "transaction_date", "=", date])

                # Retrieve the sales orders from the database
                sales_orders = frappe.get_all("Sales Order", filters=filters, fields=["name", "customer", "customer_name", "transaction_date", "status", "total_qty", "grand_total", "total_taxes_and_charges", "address_display", "docstatus"])

                sales_orders_list = []
                count = 0
                order_amount = 0.0
                outstanding = 0.0
                for sales_order in sales_orders:
                    doc=frappe.get_doc("Sales Order",sales_order.name)
                    items=[]
                    if sales_order.name:
                        count = count + 1
                    if sales_order.grand_total:
                        order_amount = order_amount + sales_order.grand_total
                    if sales_order.customer:
                        outstanding = outstanding + flt(get_party_bal(sales_order.customer))
                    for j in doc.items:
                        item=frappe.get_doc("Item",j.item_code)
                        product=""
                        site_name = get_site_name(frappe.local.request.host)
                        if item.image:
                            if "http" in str(item.image):
                                product=item.image
                            else:
                                product=str(site_name)+str(item.image)
                        items.append({"item_code":j.item_code,"qty":j.qty,"rate":j.rate,"amount":j.amount,"image":product})
                        sales_exe = frappe.db.get_value('Customer', {'name': sales_order.customer}, ['sales_executive'])
                        sales_orders_list.append({
                            "order_number": sales_order.name,
                            "customer_name": sales_order.customer_name,
                            "customer_address": sales_order.address_display,
                            "order_date": sales_order.transaction_date,
                            "order_status": sales_order.status,
                            "total_amount": sales_order.grand_total,
                            "total_taxes_and_charges": sales_order.total_taxes_and_charges,
                            "sales_executive_id": sales_exe or "",
                            "sales_executive_name": frappe.db.get_value('User', {'name': sales_exe}, ['full_name']) or "",
                            "items" : items
                        })

                response= {
                    "isSuccess":1,
                    "totalOrder":count,
                    "totalOrderAmount":order_amount,
                    "outstanding": outstanding,
                    "defaultBalance":frappe.db.get_value('Employee', {'prefered_email': sales_executive}, ['default_balance']) if sales_executive else "",
                    "message":"Sales Orders List",
                    "data": sales_orders_list
                }
                frappe.local.response["isSuccess"] = 1
                frappe.local.response["totalOrder"] = count
                frappe.local.response["totalOrderAmount"] = order_amount
                frappe.local.response["outstanding"] = outstanding
                frappe.local.response["defaultBalance"] = frappe.db.get_value('Employee', {'name': sales_executive}, ['default_balance']) if sales_executive else ""
                frappe.local.response["message"] = "Sales Orders List"
                frappe.local.response["data"] = sales_orders_list
                # return response

        else:
            sales_orders = frappe.get_all("Sales Order", fields=["name", "customer", "customer_name", "transaction_date", "status", "total_qty", "grand_total", "total_taxes_and_charges", "address_display", "docstatus"])

            sales_orders_list = []
            count = 0
            order_amount = 0.0
            outstanding = 0.0
            for sales_order in sales_orders:
                doc=frappe.get_doc("Sales Order",sales_order.name)
                items=[]
                if sales_order.name:
                    count = count + 1
                if sales_order.grand_total:
                    order_amount = order_amount + sales_order.grand_total
                if sales_order.customer:
                    outstanding = outstanding + flt(get_party_bal(sales_order.customer))
                for j in doc.items:
                    item=frappe.get_doc("Item",j.item_code)
                    product=""
                    site_name = get_site_name(frappe.local.request.host)
                    if item.image:
                        if "http" in str(item.image):
                            product=item.image
                        else:
                            product=str(site_name)+str(item.image)
                    items.append({"item_code":j.item_code,"qty":j.qty,"rate":j.rate,"amount":j.amount,"image":product})
                    sales_exe = frappe.db.get_value('Customer', {'name': sales_order.customer}, ['sales_executive'])
                    sales_orders_list.append({
                        "order_number": sales_order.name,
                        "customer_name": sales_order.customer_name,
                        "customer_address": sales_order.address_display,
                        "order_date": sales_order.transaction_date,
                        "order_status": sales_order.status,
                        "total_amount": sales_order.grand_total,
                        "total_taxes_and_charges": sales_order.total_taxes_and_charges,
                        "sales_executive_id": sales_exe or "",
                        "sales_executive_name": frappe.db.get_value('User', {'name': sales_exe}, ['full_name']) or "",
                        "items" : items
                    })

            response= {
                "isSuccess":1,
                "totalOrder":count,
                "totalOrderAmount":order_amount,
                "outstanding": outstanding,
                "defaultBalance":frappe.db.get_value('Employee', {'prefered_email': sales_executive}, ['default_balance']) if sales_executive else "",
                "message":"Sales Orders List",
                "data": sales_orders_list
            }
            
            frappe.local.response["isSuccess"] = 1
            frappe.local.response["totalOrder"] = count
            frappe.local.response["totalOrderAmount"] = order_amount
            frappe.local.response["outstanding"]= outstanding
            frappe.local.response["defaultBalance"] = frappe.db.get_value('Employee', {'name': sales_executive}, ['default_balance']) if sales_executive else ""
            frappe.local.response["message"] = "Sales Orders List"
            frappe.local.response["data"] = sales_orders_list
            # return response


    except frappe.exceptions:
        response= {
            "isSuccess":0,
            "message":frappe.get_traceback()
        }
        frappe.local.response["isSuccess"] = 0
        frappe.local.response["message"] = frappe.get_traceback()
    # return response


def get_party_bal(customer):
   cust_name =customer
   doctype = "Customer"
   loyalty_program = None

   party_bal = get_dashboard_info(doctype, cust_name, loyalty_program)

   if cust_name and party_bal:
      return party_bal[0]['total_unpaid']
   else:
      return 0.0





@frappe.whitelist()
def get_vendor_details(user_type,sales_executive=None):
    try:
        if sales_executive:
            filters = []
                    
            filters.append(["Employee", "prefered_email", "=", sales_executive])
            filters.append(["Employee", "user_type", "=", user_type])

            vendor = frappe.get_all("Employee",filters=filters , fields=["name as id","employee_name as name","cell_number as mobile","user_type","person_to_be_contacted as mobile2"])
        
        else:
            filters = []
                    
            filters.append(["Employee", "user_type", "=", user_type])
            vendor = frappe.get_all("Employee", filters=filters ,fields=["name as id","employee_name as name","cell_number as mobile","user_type","person_to_be_contacted as mobile2"])
    
        response= {
                "isSuccess":1,
                "message":"Vendor Details",
                "data":vendor
            }
        frappe.local.response["isSuccess"] = 1
        frappe.local.response["message"] = "Vendor Details"
        frappe.local.response["data"] = vendor
        # return response

    except frappe.exceptions:
        response= {
            "isSuccess":0,
            "message":frappe.get_traceback()
        }
        frappe.local.response["isSuccess"] = 0
        frappe.local.response["message"] = frappe.get_traceback()




@frappe.whitelist()
def get_sku_tonnage_details(item=None):
    try:
        if item:
            soi_doc = frappe.db.sql("""select sum(qty) as qty,item_code,item_name,image from `tabSales Order Item` where item_code="{0}" and delivery_date ="{1}" """.format(item,today()),as_dict=True)
        else:
            soi_doc = frappe.db.sql("""SELECT sum(qty) as qty,item_code,item_name,image FROM `tabSales Order Item` WHERE delivery_date ="{0}" GROUP BY item_code""".format(today()),as_dict=True)
        
        if soi_doc:
            sku_order_list= []
            total_qty = 0.0
            for vendor in soi_doc:
                total_qty = total_qty + flt(vendor.get("qty"))

                item=frappe.get_doc("Item",vendor.get("item_code"))
                product=""
                site_name = get_site_name(frappe.local.request.host)
                if item.image:
                    if "http" in str(item.image):
                        product=item.image
                    else:
                        product=str(site_name)+str(item.image)

                filters = []
                order_count = 0
                filters.append(["Sales Order Item", "item_code", "=", vendor.get("item_code")])
                filters.append(["Sales Order Item", "delivery_date", "=", today()])
                order = frappe.get_all("Sales Order Item", filters=filters, fields=["name"])
                for count in order:
                    order_count = order_count + 1

                email = frappe.db.get_list("User", {"name": frappe.session.user}, ["email"])
                warehouse = frappe.db.get_list("Employee", {"prefered_email": email}, ["warehouse"])
                item_name_conversion = frappe.db.get_list("Item Name Conversion", {"warehouse": warehouse}, ["item_name_conversion"])

                sku_order_list.append({
                    "item_code": vendor.get("item_code"),
                    "item_name": item.item_name,
                    "item_name_conversion": item_name_conversion,
                    "qty": vendor.get("qty"),
                    "image":product or "",
                    "total_order":order_count
                
                })

            response= {
                    "isSuccess":1,
                    "message":"SKU Tonnage Deatils",
                    "total_sku_qty":total_qty,
                    "date":today(),
                    "data":sku_order_list
                }
            frappe.local.response["isSuccess"] = 1
            frappe.local.response["message"] = "SKU Tonnage Deatils"
            frappe.local.response["total_sku_qty"] = total_qty
            frappe.local.response["date"] = today()
            frappe.local.response["data"] = sku_order_list
            # return response

        else:
            response= {
                "isSuccess":1,
                "message":"SKU Tonnage Deatils Does Not Exist"
            }
            frappe.local.response["isSuccess"] = 1
            frappe.local.response["message"] = "SKU Tonnage Deatils Does Not Exist"

    except frappe.exceptions:
        response= {
            "isSuccess":0,
            "message":frappe.get_traceback()
        }
        frappe.local.response["isSuccess"] = 0
        frappe.local.response["message"] = frappe.get_traceback()



@frappe.whitelist()
def get_deleted_item_list():
    try:
        email = frappe.db.get_value("User", {"name":frappe.session.user}, ["email"])
        warehouse = frappe.db.get_value("Employee", {"prefered_email": email}, ["warehouse"])
        filters = []
                    
        filters.append(["Sales Order Item", "warehouse", "=", warehouse])
        sales_orders = frappe.get_all("Sales Order", filters=filters, fields=["name"])
        del_item_list = []
        for sales_order in sales_orders:
            filters = []
                    
            filters.append(["Deleted Item Records", "sales_order", "=", sales_order])
            dir_list = frappe.get_all("Deleted Item Records", filters=filters, fields=["name"])
            for dir in dir_list:
                del_item_list.append({
                    "sales_order": dir.sales_order,
                    "item": dir.item,
                    "user": dir.user,
                    "customer": dir.customer
                })

        response= {
            "isSuccess":1,
            "message":"Deleted Item List",
            "data":del_item_list
        }
        frappe.local.response["isSuccess"] = 1
        frappe.local.response["message"] = "Deleted Item List"
        frappe.local.response["data"] = del_item_list


    except frappe.exceptions:
        response= {
            "isSuccess":0,
            "message":frappe.get_traceback()
        }
        frappe.local.response["isSuccess"] = 0
        frappe.local.response["message"] = frappe.get_traceback()     
    


# #Supplier Creation Api
# @frappe.whitelist()
# def create_supplier(email,name, mobile,zip,city,state,country,grade,street,street2,area,sale_executive_id,image,lat,long):
# #    return email,name, mobile,zip,city,state,country,grade,street,street2,area,sale_executive_id,image,lat,long    
#    try:
#       cus=frappe.db.get_value("Supplier",{"mobile_no":mobile},"name")
#       if cus:
#          response = {
#             "isSuccess":0,
#             "message":"Supplier Already Exist"
#          }
#          frappe.local.response["isSuccess"] = 0
#          frappe.local.response["message"] = "Supplier Already Exist"
#          # return response
#       from frappe.utils import validate_phone_number
#       p=validate_phone_number(mobile)
#       if p=="False":
#          response = {
#             "isSuccess":0,
#             "message":"Invalid Phone No"
#          }
#          frappe.local.response["isSuccess"] = 0
#          frappe.local.response["message"] = "Invalid Phone No"
#          # return response

#       from frappe.utils import validate_email_address
#       eno=validate_email_address(email)
#       if eno=="False":
#          response = {
#             "isSuccess":0,
#             "message":"Invalid Email No"
#          }
#          frappe.local.response["isSuccess"] = 0
#          frappe.local.response["message"] = "Invalid Email No"
         
#          # return response


      
#       supplier = frappe.new_doc("Supplier")
#       supplier.se_user=frappe.session.user
#       supplier.supplier_name = name
#       supplier.email_id = email
#       supplier.supplier_type = 'Individual'
#       supplier.territory = area
#       # supplier.image=image
#       supplier.lat=flt(lat)
#       supplier.long=flt(long)
#       supplier.supplier_group = grade
#       supplier.insert(ignore_permissions=True)

#       contact = frappe.new_doc("Contact")
#       contact.first_name = name   
#       contact.append("phone_nos",{
#       "phone": mobile, "is_primary_mobile_no":1
#       })

#       contact.append("email_ids",{
#       "email_id": email, "is_primary":1
#       })
#       contact.insert(ignore_permissions=True)
#       supplier.supplier_primary_contact=contact.name
#       supplier.save(ignore_permissions=True)
#       address = frappe.new_doc("Address")
#       address.address_title = name
#       address.city = city
#       address.pincode = zip
#       address.country = "India"
#       address.state = state
#       address.address_type = "Billing"
#       address.address_line1 = street
#       address.address_line2 = street2
#       address.insert(ignore_permissions=True)
#       address.append("links",{
#       "link_doctype":"Supplier", "link_name":supplier.name
#       })
#       address.save(ignore_permissions=True)
#       supplier.supplier_primary_address=address.name
#       supplier.save(ignore_permissions=True)

#       use = frappe.new_doc("User")
#       use.email = email
#       use.first_name = name
#       use.mobile_no = mobile
#       use.user_type = "System User"

#       use.insert(ignore_permissions=True)
      
#       response= {
#          "isSuccess":1,
#          "message":"Supplier registered successfully",
#       }
#       frappe.local.response["isSuccess"] = 1
#       frappe.local.response["message"] = "Supplier registered successfully"
#       # frappe.local.response["data"] = supplier
#       # return response
#    except frappe.exceptions:
#       response = {
#          "isSuccess":0,
#          "message":frappe.get_traceback()
#       }
#       frappe.local.response["isSuccess"] = 0
#       frappe.local.response["message"] = frappe.get_traceback()
#       # return response

