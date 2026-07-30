import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)
	show_salary_structure_title_in_links()
	backfill_salary_structure_titles()


def get_custom_fields():
	return {
		"Salary Structure": [
			{
				"fieldname": "custom_salary_structure_title",
				"fieldtype": "Data",
				"label": "Salary Structure Title",
				"in_list_view": 1,
				"in_standard_filter": 1,
				"insert_after": "company",
				"description": "User-facing title shown with the Salary Structure ID in Link fields.",
			},
		]
	}


def show_salary_structure_title_in_links():
	make_property_setter(
		"Salary Structure",
		None,
		"title_field",
		"Data",
		"custom_salary_structure_title",
	)
	make_property_setter("Salary Structure", None, "show_title_field_in_link", "Check", "1")
	make_property_setter("Salary Structure", None, "search_fields", "Data", "custom_salary_structure_title")


def backfill_salary_structure_titles():
	for salary_structure in frappe.get_all(
		"Salary Structure",
		filters={"custom_salary_structure_title": ["in", ["", None]]},
		pluck="name",
	):
		frappe.db.set_value(
			"Salary Structure",
			salary_structure,
			"custom_salary_structure_title",
			salary_structure,
			update_modified=False,
		)


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
			"doctype_or_field": "DocType" if not field_name else "DocField",
			"doc_type": doc_type,
			"field_name": field_name,
			"property": property_name,
			"property_type": property_type,
			"value": value,
		}
	).insert(ignore_permissions=True)
