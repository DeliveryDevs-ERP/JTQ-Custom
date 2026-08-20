from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Employee": [
			{
				"fieldname": "custom_income_tax_slab",
				"fieldtype": "Link",
				"label": "Income Tax Slab",
				"options": "Income Tax Slab",
				"insert_after": "custom_current_salary_structure_assignment",
			},
		]
	}
