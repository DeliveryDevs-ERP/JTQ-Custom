from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Payroll Entry": [
			{
				"fieldname": "custom_jtq_payroll_filters_section",
				"fieldtype": "Section Break",
				"label": "JTQ Payroll Filters",
				"insert_after": "designation",
			},
			{
				"fieldname": "custom_work_mode",
				"fieldtype": "Link",
				"label": "Work Mode",
				"options": "Work Mode",
				"insert_after": "custom_jtq_payroll_filters_section",
			},
			{
				"fieldname": "custom_city",
				"fieldtype": "Link",
				"label": "City",
				"options": "City",
				"insert_after": "custom_work_mode",
			},
			{
				"fieldname": "custom_province",
				"fieldtype": "Link",
				"label": "Province",
				"options": "Province",
				"insert_after": "custom_city",
			},
			{
				"fieldname": "custom_location_column_break",
				"fieldtype": "Column Break",
				"insert_after": "custom_province",
			},
			{
				"fieldname": "custom_country",
				"fieldtype": "Link",
				"label": "Country",
				"options": "Country",
				"insert_after": "custom_location_column_break",
			},
			{
				"fieldname": "custom_region",
				"fieldtype": "Link",
				"label": "Region",
				"options": "Region",
				"insert_after": "custom_country",
			},
			{
				"fieldname": "custom_madrasa",
				"fieldtype": "Link",
				"label": "Madrasa",
				"options": "Madrasa",
				"insert_after": "custom_region",
			},
		]
	}
