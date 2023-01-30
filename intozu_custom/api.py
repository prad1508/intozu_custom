import json
import frappe

@frappe.whitelist()
def add_lead(lead_name,email_id,mobile_no,source,notes):
    try:
        doc = frappe.new_doc("Lead")
        doc.lead_name = lead_name
        doc.email_id = email_id
        doc.source = source
        doc.mobile_no = mobile_no
        doc.notes = notes
        doc.status = "Lead"
        doc.ignore_permissions = True
        doc.save()
        lead = "Lead Source Added Successfully"

        return lead

    except Exception as e:

        return e