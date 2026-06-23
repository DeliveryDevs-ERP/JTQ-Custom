from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Leave Type": [
			{
				"fieldname": "custom_min_working_hours_for_compensatory_leave",
				"fieldtype": "Float",
				"label": "Minimum Working Hours for Compensatory Leave",
				"default": "6",
				"precision": "2",
				"depends_on": "eval:doc.is_compensatory",
				"description": "Attendance must have working hours greater than this value for Compensatory Leave Request. Set 0 to disable this check.",
				"insert_after": "is_compensatory",
			},
		]
	}
