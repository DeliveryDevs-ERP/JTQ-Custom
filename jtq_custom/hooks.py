app_name = "jtq_custom"
app_title = "JTQ Custom"
app_publisher = "JTQ"
app_description = "JTQ Customizations for ERPNext and HRMS"
app_email = "admin@example.com"
app_license = "mit"

fixtures = [
	{
		"dt": "Print Format",
		"filters": [
			[
				"name",
				"in",
				[
					"Appointment letter for Back Office",
					"Appointment Letter For Field Staff",
				],
			]
		],
	},
]

doctype_js = {
	"Attendance": "public/js/attendance.js",
	"Attendance Request": "public/js/attendance_request.js",
	"Compensatory Leave Request": "public/js/compensatory_leave_request.js",
	"Employee": "public/js/employee.js",
	"JTQ Bulk Attendance": "public/js/jtq_bulk_attendance.js",
	"Payroll Entry": "public/js/payroll_entry.js",
	"Salary Structure": "public/js/salary_structure.js",
}

doctype_list_js = {
	"Attendance": "public/js/attendance_list.js",
}

override_doctype_class = {
	"Compensatory Leave Request": "jtq_custom.overrides.compensatory_leave_request.JTQCompensatoryLeaveRequest",
	"Payroll Entry": "jtq_custom.overrides.payroll_entry.JTQPayrollEntry",
	"Salary Slip": "jtq_custom.overrides.salary_slip.JTQSalarySlip",
	"Salary Structure": "jtq_custom.overrides.salary_structure.JTQSalaryStructure",
}

override_whitelisted_methods = {
	"hrms.payroll.doctype.payroll_entry.payroll_entry.employee_query": "jtq_custom.overrides.payroll_entry.employee_query",
}

doc_events = {
	"Attendance": {
		"before_validate": "jtq_custom.attendance.calculate_attendance_time_fields",
		"before_submit": "jtq_custom.attendance.calculate_overtime_and_attendance_details",
	},
	"Attendance Request": {
		"on_submit": "jtq_custom.attendance.update_attendance_times_from_request",
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
	"jtq_custom.patches.add_attendance_request_time_fields.execute",
	"jtq_custom.patches.update_custom_master_fields.execute",
	"jtq_custom.patches.add_compensatory_leave_working_hours_field.execute",
	"jtq_custom.patches.add_employee_salary_structure_assignment_fields.execute",
	"jtq_custom.patches.add_compensatory_leave_allocation_reference.execute",
]
