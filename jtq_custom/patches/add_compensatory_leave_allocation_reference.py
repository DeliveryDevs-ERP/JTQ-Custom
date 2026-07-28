import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_field_name = "Leave Allocation-custom_compensatory_leave_request"
	if frappe.db.exists("Custom Field", custom_field_name):
		fieldtype = frappe.db.get_value("Custom Field", custom_field_name, "fieldtype")
		if fieldtype != "Data":
			# Link fields trigger Frappe's linked-document cancel prompt. This is only
			# an internal tracker, so keep it as plain Data.
			frappe.db.set_value(
				"Custom Field",
				custom_field_name,
				{"fieldtype": "Data", "options": None},
				update_modified=False,
			)

	create_custom_fields(
		{
			"Leave Allocation": [
				{
					"fieldname": "custom_compensatory_leave_request",
					"fieldtype": "Data",
					"label": "Compensatory Leave Request",
					"insert_after": "description",
					"read_only": 1,
					"hidden": 1,
					"no_copy": 1,
				},
			]
		},
		update=True,
	)
