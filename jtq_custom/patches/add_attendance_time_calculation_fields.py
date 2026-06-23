from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Attendance": [
			{
				"fieldname": "custom_shift_hours",
				"fieldtype": "Float",
				"label": "Shift Hours",
				"precision": "2",
				"read_only": 1,
				"insert_after": "working_hours",
			},
			{
				"fieldname": "custom_late_entry_detail",
				"fieldtype": "Data",
				"label": "Late Entry Detail",
				"read_only": 1,
				"insert_after": "late_entry",
			},
			{
				"fieldname": "custom_late_entry_hours",
				"fieldtype": "Float",
				"label": "Late Entry Hours",
				"precision": "2",
				"read_only": 1,
				"insert_after": "custom_late_entry_detail",
			},
			{
				"fieldname": "custom_early_exit_detail",
				"fieldtype": "Data",
				"label": "Early Exit Detail",
				"read_only": 1,
				"insert_after": "early_exit",
			},
			{
				"fieldname": "custom_early_exit_hours",
				"fieldtype": "Float",
				"label": "Early Exit Hours",
				"precision": "2",
				"read_only": 1,
				"insert_after": "custom_early_exit_detail",
			},
			{
				"fieldname": "custom_overtime_detail",
				"fieldtype": "Data",
				"label": "Overtime Detail",
				"read_only": 1,
				"insert_after": "custom_early_exit_hours",
			},
			{
				"fieldname": "custom_overtime_hours",
				"fieldtype": "Float",
				"label": "Overtime Hours",
				"precision": "2",
				"read_only": 1,
				"insert_after": "custom_overtime_detail",
			},
		]
	}
