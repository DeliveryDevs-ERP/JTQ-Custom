import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	employee_fields = [
		{
			"fieldname": "custom_madrasa",
			"fieldtype": "Link",
			"label": "Madrasa",
			"options": "Madrasa",
			"insert_after": "branch",
		},
		{
			"fieldname": "custom_city",
			"fieldtype": "Link",
			"label": "City",
			"options": "City",
			"insert_after": "custom_madrasa",
		},
		{
			"fieldname": "custom_province",
			"fieldtype": "Link",
			"label": "Province",
			"options": "Province",
			"insert_after": "custom_city",
		},
		{
			"fieldname": "custom_country",
			"fieldtype": "Link",
			"label": "Country",
			"options": "Country",
			"insert_after": "custom_province",
		},
		{
			"fieldname": "custom_work_mode",
			"fieldtype": "Link",
			"label": "Work Mode",
			"options": "Work Mode",
			"insert_after": "custom_country",
		},
	]

	if frappe.db.exists("Custom Field", {"dt": "Employee", "fieldname": "custom_city"}):
		employee_fields = [field for field in employee_fields if field["fieldname"] != "custom_city"]

	return {"Employee": employee_fields}
