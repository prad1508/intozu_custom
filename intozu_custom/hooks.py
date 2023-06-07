from . import __version__ as app_version

app_name = "intozu_custom"
app_title = "Intozu Custom"
app_publisher = "Stackerbee"
app_description = "Intozu Custom App"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@stackerbee.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/intozu_custom/css/intozu_custom.css"
# app_include_js = "/assets/intozu_custom/js/intozu_custom.js"

# include js, css files in header of web template
# web_include_css = "/assets/intozu_custom/css/intozu_custom.css"
# web_include_js = "/assets/intozu_custom/js/intozu_custom.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "intozu_custom/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
    "Purchase Receipt" : "public/js/purchase_receipt.js",
	"Work Order" : "public/js/work_order.js",
	# "Stock Entry" : "public/js/stock_entry.js",
}
doctype_list_js = {
	"Purchase Receipt" : "public/js/purchase_receipt_list.js",
	"Purchase Order" : "public/js/purchase_order_list.js",
}
# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "intozu_custom.install.before_install"
# after_install = "intozu_custom.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "intozu_custom.uninstall.before_uninstall"
# after_uninstall = "intozu_custom.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "intozu_custom.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"Event": "intozu_custom.utils.stock_ledger_entry.Event"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }
doc_events = {
	"Purchase Receipt": {
		"before_update_after_submit": "intozu_custom.utils.purchase_receipt.qrcode_generate",
		"on_update" :"intozu_custom.utils.purchase_receipt.update_pendding_qty_on_po",
		"on_submit" : "intozu_custom.utils.purchase_order.on_update_pr_change_status",
		# "on_cancel" : "intozu_custom.utils.purchase_order.on_cancel_pr_change_status"
	},
	"Work Order":{
		"before_update_after_submit":"intozu_custom.utils.work_order.qrcode_generate",
	},
	"Stock Entry": {
		"on_update" : "intozu_custom.utils.stock_entry.update_pendding_qty",
		"on_submit" : "intozu_custom.utils.stock_entry.on_update_se_change_status",
	},
	"Purchase Order":{
		"on_update_after_submit" : "intozu_custom.utils.purchase_order.on_update_po_change_status",
		"on_cancel":"intozu_custom.utils.purchase_order.on_cancel_po_change_status",
	},
	"Pick List":{
		"before_submit" : "intozu_custom.utils.pick_list.create_stock_entry_onsubmit",
		"on_submit" : "intozu_custom.utils.pick_list.on_submit_so_change_status",
		"on_update":"intozu_custom.utils.pick_list.update_pennding_picked_qty_so",
		"on_cancel" : "intozu_custom.utils.pick_list.on_cancel_so_confirm_status",
		"on_trash" : "intozu_custom.utils.pick_list.on_cancel_so_confirm_status",
	},
	"Stock Ledger Entry":{
		"before_insert":"intozu_custom.utils.stock_ledger_entry.get_data_in_wle",
	},
}
# before_update_after_submit
# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"intozu_custom.tasks.all"
#	],
#	"daily": [
#		"intozu_custom.tasks.daily"
#	],
#	"hourly": [
#		"intozu_custom.tasks.hourly"
#	],
#	"weekly": [
#		"intozu_custom.tasks.weekly"
#	]
#	"monthly": [
#		"intozu_custom.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "intozu_custom.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "intozu_custom.event.get_events"
# }
override_whitelisted_methods = {
	"erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt": "intozu_custom.utils.purchase_receipt.make_purchase_receipt",
	"erpnext.selling.page.point_of_sale.point_of_sale.search_for_serial_or_batch_or_barcode_number": "intozu_custom.utils.purchase_receipt.search_for_serial_or_batch_or_barcode_number",
	"erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_stock_entry" : "intozu_custom.utils.purchase_receipt.make_stock_entry",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "intozu_custom.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"intozu_custom.auth.validate"
# ]

