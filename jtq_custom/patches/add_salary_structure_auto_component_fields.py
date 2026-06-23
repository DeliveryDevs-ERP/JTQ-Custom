from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Salary Detail": [
			{
				"fieldname": "custom_jtq_auto_populated",
				"fieldtype": "Check",
				"label": "JTQ Auto Populated",
				"hidden": 1,
				"no_copy": 1,
				"insert_after": "additional_salary",
			},
			{
				"fieldname": "custom_jtq_amount_changed",
				"fieldtype": "Check",
				"label": "JTQ Amount Changed",
				"hidden": 1,
				"no_copy": 1,
				"insert_after": "custom_jtq_auto_populated",
			},
		]
	}
