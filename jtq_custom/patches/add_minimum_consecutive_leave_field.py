from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Leave Type": [
			{
				"fieldname": "custom_min_consecutive_leaves_allowed",
				"fieldtype": "Int",
				"label": "Minimum Consecutive Leaves Allowed",
				"non_negative": 1,
				"description": (
					"Minimum number of consecutive leave days an Employee can apply for. "
					"Set 0 to disable this check."
				),
				"insert_after": "max_continuous_days_allowed",
			},
		]
	}
