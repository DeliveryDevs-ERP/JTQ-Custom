import json

import frappe


def execute():
	remove_salary_column_break()
	remove_salary_breaks_from_field_order()
	frappe.clear_cache(doctype="Employee")


def remove_salary_column_break():
	if frappe.db.exists("Custom Field", "Employee-salary_cb"):
		frappe.delete_doc("Custom Field", "Employee-salary_cb", force=1, ignore_permissions=True)


def remove_salary_breaks_from_field_order():
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
	cleaned_order = [field for field in field_order if field not in {"salary_cb", "column_break_lhiy"}]

	if cleaned_order != field_order:
		frappe.db.set_value("Property Setter", property_setter, "value", json.dumps(cleaned_order))
