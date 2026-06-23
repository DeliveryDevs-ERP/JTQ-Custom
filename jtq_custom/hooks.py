app_name = "jtq_custom"
app_title = "JTQ Custom"
app_publisher = "JTQ"
app_description = "JTQ Customizations for ERPNext and HRMS"
app_email = "admin@example.com"
app_license = "mit"

doctype_js = {
	"Attendance": "public/js/attendance.js",
	"JTQ Bulk Attendance": "public/js/jtq_bulk_attendance.js",
	"Salary Structure": "public/js/salary_structure.js",
}

doctype_list_js = {
	"Attendance": "public/js/attendance_list.js",
}

override_doctype_class = {
	"Payroll Entry": "jtq_custom.overrides.payroll_entry.JTQPayrollEntry",
	"Salary Slip": "jtq_custom.overrides.salary_slip.JTQSalarySlip",
	"Salary Structure": "jtq_custom.overrides.salary_structure.JTQSalaryStructure",
}

doc_events = {
	"Attendance": {
		"before_validate": "jtq_custom.attendance.calculate_attendance_time_fields",
	},
	"City": {
		"validate": "jtq_custom.master_utils.set_master_id",
	},
	"Compensatory Leave Request": {
		"validate": "jtq_custom.compensatory_leave.validate_compensatory_leave_working_hours",
	},
	"Province": {
		"validate": "jtq_custom.master_utils.set_master_id",
	},
	"Additional Salary": {
		"before_validate": "jtq_custom.payroll.sync_additional_salary_controls",
		"before_update_after_submit": "jtq_custom.payroll.sync_additional_salary_controls",
	},
	"Salary Slip": {
		"on_submit": "jtq_custom.payroll.sync_advance_recovery_from_salary_slip",
		"on_cancel": "jtq_custom.payroll.sync_advance_recovery_from_salary_slip",
	},
	"Salary Structure": {
		"before_insert": "jtq_custom.payroll.populate_salary_structure_components",
	},
}

after_install = "jtq_custom.patches.add_bulk_attendance_custom_fields.execute"
after_migrate = [
	"jtq_custom.patches.add_bulk_attendance_custom_fields.execute",
	"jtq_custom.patches.add_payroll_entry_location_fields.execute",
	"jtq_custom.patches.add_employee_location_work_mode_fields.execute",
	"jtq_custom.patches.add_advance_salary_recovery_controls.execute",
	"jtq_custom.patches.add_salary_structure_auto_component_fields.execute",
	"jtq_custom.patches.add_attendance_time_calculation_fields.execute",
	"jtq_custom.patches.update_custom_master_fields.execute",
	"jtq_custom.patches.add_compensatory_leave_working_hours_field.execute",
]
