frappe.listview_settings['Purchase Order'] = {
	add_fields: ["supplier_name", "status", "intozi_status", "transaction_date",
		"base_grand_total", "per_billed", "status", "order_type", "name", "skip_delivery_note"],
	get_indicator: function (doc) {
		if (doc.status === "Closed") {
			// Closed
			return [__("Closed"), "green", "status,=,Closed"];
		} else if (doc.status === "On Hold") {
			// on hold
			return [__("On Hold"), "orange", "status,=,On Hold"];
		}else if (doc.intozi_status === "Partially Receipt") {
            return [__("Partially Receipt"), "orange", "status,=,Partially Receipt"];
        }else if(doc.intozi_status === "Completely Receipt"){
            return [__("Completely Receipt"), "green", "status,=,Completely Receipt"];
        }else if(doc.intozi_status === "Short Close"){
            return [__("Short Close"), "orange", "status,=,Short Close"];
        }else if(doc.intozi_status === "Confirmed For Submitted"){
            return [__("Confirmed For Submitted"), "green", "status,=,Confirmed For Submitted"];
        }else if(doc.intozi_status === "Cancelled"){
            return [__("Cancelled"), "green", "status,=,Cancelled"];
        }
	}
};