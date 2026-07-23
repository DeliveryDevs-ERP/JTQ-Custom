from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Attendance Request": [
				{
					"fieldname": "custom_in_time",
					"fieldtype": "Time",
					"label": "Employee In Time",
					"insert_after": "to_date",
				},
				{
					"fieldname": "custom_out_time",
					"fieldtype": "Time",
					"label": "Employee Out Time",
					"insert_after": "custom_in_time",
				},
			]
		},
		update=True,
	)
