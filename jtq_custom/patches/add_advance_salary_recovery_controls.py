import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)
	update_additional_salary_property_setters()


def get_custom_fields():
	return {
		"Additional Salary": [
			{
				"fieldname": "custom_adjustment_section",
				"fieldtype": "Section Break",
				"label": "Adjustment Controls",
				"insert_after": "amount",
			},
			{
				"fieldname": "custom_adjustment_type",
				"fieldtype": "Select",
				"label": "Adjustment Type",
				"options": "\nRegular\nAdvance Recovery\nOvertime\nSalary Excess",
				"insert_after": "custom_adjustment_section",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_paused",
				"fieldtype": "Check",
				"label": "Paused",
				"insert_after": "custom_adjustment_type",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_overtime_hours",
				"fieldtype": "Float",
				"label": "Overtime Hours",
				"depends_on": "eval:doc.custom_adjustment_type == 'Overtime'",
				"insert_after": "custom_paused",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_overtime_rate",
				"fieldtype": "Currency",
				"label": "Overtime Rate",
				"options": "currency",
				"depends_on": "eval:doc.custom_adjustment_type == 'Overtime'",
				"insert_after": "custom_overtime_hours",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_balance_column",
				"fieldtype": "Column Break",
				"insert_after": "custom_overtime_rate",
			},
			{
				"fieldname": "custom_total_adjustment_amount",
				"fieldtype": "Currency",
				"label": "Total Principal Amount",
				"options": "currency",
				"insert_after": "custom_balance_column",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_paid_or_deducted_amount",
				"fieldtype": "Currency",
				"label": "Recovered Amount",
				"options": "currency",
				"read_only": 1,
				"insert_after": "custom_total_adjustment_amount",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_remaining_balance",
				"fieldtype": "Currency",
				"label": "Pending Recovery Balance",
				"options": "currency",
				"read_only": 1,
				"insert_after": "custom_paid_or_deducted_amount",
				"allow_on_submit": 1,
			},
		]
	}


def update_additional_salary_property_setters():
	for fieldname in (
		"amount",
		"from_date",
		"to_date",
		"payroll_date",
		"disabled",
	):
		make_property_setter(fieldname, "allow_on_submit", "Check", "1")


def make_property_setter(fieldname, property_name, property_type, value):
	filters = {
		"doc_type": "Additional Salary",
		"field_name": fieldname,
		"property": property_name,
	}
	if frappe.db.exists("Property Setter", filters):
		property_setter = frappe.get_doc("Property Setter", filters)
		property_setter.value = value
		property_setter.save(ignore_permissions=True)
		return

	frappe.get_doc(
		{
			"doctype": "Property Setter",
			"doctype_or_field": "DocField",
			"doc_type": "Additional Salary",
			"field_name": fieldname,
			"property": property_name,
			"property_type": property_type,
			"value": value,
		}
	).insert(ignore_permissions=True)
