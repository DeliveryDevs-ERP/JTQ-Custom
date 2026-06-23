import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	normalize_existing_fieldtypes()
	create_custom_fields(get_custom_fields(), update=True)
	normalize_employee_custom_fields()


def get_custom_fields():
	employee_fields = [
		{
			"fieldname": "custom_jtq_details_section",
			"fieldtype": "Section Break",
			"label": "JTQ Details",
			"insert_after": "employment_details",
		},
		{
			"fieldname": "custom_madrasa",
			"fieldtype": "Link",
			"label": "Madrasa",
			"options": "Madrasa",
			"insert_after": "custom_jtq_details_section",
		},
		{
			"fieldname": "custom_region",
			"fieldtype": "Link",
			"label": "Region",
			"options": "Region",
			"insert_after": "custom_madrasa",
		},
		{
			"fieldname": "custom_city",
			"fieldtype": "Link",
			"label": "City",
			"options": "City",
			"insert_after": "custom_region",
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
		{
			"fieldname": "custom_payroll_group",
			"fieldtype": "Link",
			"label": "Payroll Group",
			"options": "Payroll Group",
			"insert_after": "custom_work_mode",
		},
	]

	return {"Employee": employee_fields}


def normalize_employee_custom_fields():
	field_definitions = get_custom_fields()["Employee"]
	for field in field_definitions:
		custom_field_name = f"Employee-{field['fieldname']}"
		if not frappe.db.exists("Custom Field", custom_field_name):
			continue

		doc = frappe.get_doc("Custom Field", custom_field_name)
		changed = False
		for key, value in field.items():
			if doc.get(key) != value:
				doc.set(key, value)
				changed = True

		if doc.reqd:
			doc.reqd = 0
			changed = True

		if doc.hidden:
			doc.hidden = 0
			changed = True

		if changed:
			doc.save(ignore_permissions=True)


def normalize_existing_fieldtypes():
	for field in get_custom_fields()["Employee"]:
		custom_field_name = f"Employee-{field['fieldname']}"
		if not frappe.db.exists("Custom Field", custom_field_name):
			continue

		values = {}
		for key in ("fieldtype", "options"):
			if key in field:
				values[key] = field[key]

		if values:
			frappe.db.set_value(
				"Custom Field",
				custom_field_name,
				values,
				update_modified=False,
			)
