from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Employee": [
			{
				"fieldname": "custom_bank_branch_code",
				"fieldtype": "Data",
				"label": "Bank Branch Code",
				"insert_after": "bank_ac_no",
			},
			{
				"fieldname": "custom_bank_branch_address",
				"fieldtype": "Small Text",
				"label": "Bank Branch Address",
				"insert_after": "custom_bank_branch_code",
			},
		]
	}
