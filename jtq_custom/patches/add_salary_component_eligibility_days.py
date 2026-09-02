import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


FIELDNAME = "custom_eligibility_after_days"
MEDICAL_ALLOWANCE_COMPONENT = "Medical Allowance"


def execute():
	field_was_missing = not frappe.db.exists(
		"Custom Field",
		{"dt": "Salary Component", "fieldname": FIELDNAME},
	)

	create_custom_fields(get_custom_fields(), update=True)

	if field_was_missing and frappe.db.exists("Salary Component", MEDICAL_ALLOWANCE_COMPONENT):
		frappe.db.set_value(
			"Salary Component",
			MEDICAL_ALLOWANCE_COMPONENT,
			FIELDNAME,
			180,
			update_modified=False,
		)


def get_custom_fields():
	return {
		"Salary Component": [
			{
				"fieldname": FIELDNAME,
				"fieldtype": "Int",
				"label": "Eligibility After Days",
				"default": "0",
				"non_negative": 1,
				"depends_on": 'eval:doc.type == "Earning"',
				"insert_after": "remove_if_zero_valued",
				"description": (
					"Number of completed days from the Employee Date of Joining required "
					"before this earning is included in a Salary Slip. Use 0 for immediate eligibility."
				),
			},
		]
	}
