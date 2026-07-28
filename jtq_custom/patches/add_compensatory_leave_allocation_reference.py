from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Leave Allocation": [
				{
					"fieldname": "custom_compensatory_leave_request",
					"fieldtype": "Link",
					"label": "Compensatory Leave Request",
					"options": "Compensatory Leave Request",
					"insert_after": "description",
					"read_only": 1,
					"hidden": 1,
					"no_copy": 1,
				},
			]
		},
		update=True,
	)
