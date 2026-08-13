from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Employee": [
			{
				"fieldname": "custom_religious_qualification_section",
				"fieldtype": "Section Break",
				"label": "Religious Qualification",
				"insert_after": "education",
			},
			{
				"fieldname": "custom_religious_qualification",
				"fieldtype": "Table",
				"label": "Religious Qualification",
				"options": "Employee Religious Qualification",
				"insert_after": "custom_religious_qualification_section",
			},
		]
	}
