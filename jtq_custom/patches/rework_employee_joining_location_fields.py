import json

import frappe


REMOVED_JOINING_FIELDS = {
	"custom_country",
	"custom_province",
	"custom_city",
	"custom_region",
	"custom_employment_type",
}


def execute():
	remove_duplicate_joining_fields()
	move_work_mode_to_overview()
	clean_employee_field_order()
	frappe.clear_cache(doctype="Employee")


def remove_duplicate_joining_fields():
	for fieldname in REMOVED_JOINING_FIELDS:
		custom_field = f"Employee-{fieldname}"
		if frappe.db.exists("Custom Field", custom_field):
			frappe.delete_doc("Custom Field", custom_field, force=1, ignore_permissions=True)


def move_work_mode_to_overview():
	if frappe.db.exists("Custom Field", "Employee-custom_work_mode"):
		frappe.db.set_value(
			"Custom Field",
			"Employee-custom_work_mode",
			{
				"insert_after": "region",
				"hidden": 0,
				"reqd": 0,
			},
			update_modified=False,
		)

	if frappe.db.exists("Custom Field", "Employee-custom_payroll_group"):
		frappe.db.set_value(
			"Custom Field",
			"Employee-custom_payroll_group",
			{"insert_after": "custom_madrasa"},
			update_modified=False,
		)


def clean_employee_field_order():
	property_setter = frappe.db.exists(
		"Property Setter",
		{
			"doc_type": "Employee",
			"doctype_or_field": "DocType",
			"property": "field_order",
		},
	)
	if not property_setter:
		return

	value = frappe.db.get_value("Property Setter", property_setter, "value")
	if not value:
		return

	field_order = json.loads(value)
	field_order = [field for field in field_order if field not in REMOVED_JOINING_FIELDS]

	field_order = move_after(field_order, "custom_work_mode", "region")
	field_order = move_after(field_order, "custom_payroll_group", "custom_madrasa")

	frappe.db.set_value("Property Setter", property_setter, "value", json.dumps(field_order))


def move_after(field_order, fieldname, insert_after):
	if fieldname not in field_order or insert_after not in field_order:
		return field_order

	cleaned = [field for field in field_order if field != fieldname]
	insert_at = cleaned.index(insert_after) + 1
	cleaned.insert(insert_at, fieldname)
	return cleaned
