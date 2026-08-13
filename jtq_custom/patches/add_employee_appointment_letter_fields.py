from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Employee": [
			{
				"fieldname": "custom_father_name",
				"fieldtype": "Data",
				"label": "Father Name",
				"insert_after": "employee_name",
			},
		]
	}
