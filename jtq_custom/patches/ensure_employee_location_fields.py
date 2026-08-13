import json

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


EMPLOYEE_LOCATION_FIELDS = [
	{
		"fieldname": "country",
		"fieldtype": "Link",
		"label": "Country",
		"options": "Country",
		"insert_after": "column_break_25",
	},
	{
		"fieldname": "province",
		"fieldtype": "Link",
		"label": "Province",
		"options": "Province",
		"insert_after": "country",
	},
	{
		"fieldname": "city",
		"fieldtype": "Link",
		"label": "City",
		"options": "City",
		"insert_after": "province",
	},
	{
		"fieldname": "region",
		"fieldtype": "Link",
		"label": "Region",
		"options": "Region",
		"insert_after": "city",
	},
]


def execute():
	ensure_location_fields()
	ensure_location_fields_visible()
	update_employee_field_order()
	frappe.clear_cache(doctype="Employee")


def ensure_location_fields():
	meta = frappe.get_meta("Employee")
	missing_fields = [field for field in EMPLOYEE_LOCATION_FIELDS if not meta.has_field(field["fieldname"])]

	if missing_fields:
		create_custom_fields({"Employee": missing_fields}, update=True)


def ensure_location_fields_visible():
	for field in EMPLOYEE_LOCATION_FIELDS:
		fieldname = field["fieldname"]
		custom_field = f"Employee-{fieldname}"

		if frappe.db.exists("Custom Field", custom_field):
			frappe.db.set_value(
				"Custom Field",
				custom_field,
				{"hidden": 0, "read_only": 0, "insert_after": field["insert_after"]},
				update_modified=False,
			)

		make_property_setter("Employee", fieldname, "hidden", "Check", "0")


def update_employee_field_order():
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
	for field in ("country", "province", "city", "region", "custom_work_mode"):
		if field not in field_order:
			field_order.append(field)

	field_order = move_after(field_order, "country", "column_break_25")
	field_order = move_after(field_order, "province", "country")
	field_order = move_after(field_order, "city", "province")
	field_order = move_after(field_order, "region", "city")
	field_order = move_after(field_order, "custom_work_mode", "region")

	frappe.db.set_value("Property Setter", property_setter, "value", json.dumps(field_order))


def move_after(field_order, fieldname, insert_after):
	if fieldname not in field_order or insert_after not in field_order:
		return field_order

	cleaned = [field for field in field_order if field != fieldname]
	insert_at = cleaned.index(insert_after) + 1
	cleaned.insert(insert_at, fieldname)
	return cleaned


def make_property_setter(doc_type, field_name, property_name, property_type, value):
	filters = {
		"doc_type": doc_type,
		"field_name": field_name,
		"property": property_name,
	}
	if frappe.db.exists("Property Setter", filters):
		property_setter = frappe.get_doc("Property Setter", filters)
		if property_setter.value != value:
			property_setter.value = value
			property_setter.save(ignore_permissions=True)
		return

	frappe.get_doc(
		{
			"doctype": "Property Setter",
			"doctype_or_field": "DocField",
			"doc_type": doc_type,
			"field_name": field_name,
			"property": property_name,
			"property_type": property_type,
			"value": value,
		}
	).insert(ignore_permissions=True)
