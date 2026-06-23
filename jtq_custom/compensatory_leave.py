import frappe
from frappe import _
from frappe.utils import flt, format_date


MIN_WORKING_HOURS_FIELD = "custom_min_working_hours_for_compensatory_leave"


def validate_compensatory_leave_working_hours(doc, method=None):
	if not doc.employee or not doc.leave_type or not doc.work_from_date or not doc.work_end_date:
		return

	if not frappe.db.get_value("Leave Type", doc.leave_type, "is_compensatory"):
		return

	min_working_hours = get_min_working_hours(doc.leave_type)
	if min_working_hours <= 0:
		return

	attendance_records = frappe.get_all(
		"Attendance",
		filters={
			"employee": doc.employee,
			"attendance_date": ["between", (doc.work_from_date, doc.work_end_date)],
			"status": ("in", ["Present", "Work From Home", "Half Day"]),
			"docstatus": 1,
		},
		fields=["name", "attendance_date", "working_hours"],
		order_by="attendance_date asc",
	)

	invalid_records = [
		record
		for record in attendance_records
		if flt(record.working_hours) <= min_working_hours
	]

	if not invalid_records:
		return

	details = ", ".join(
		[
			_("{0} ({1} hrs)").format(
				frappe.bold(format_date(record.attendance_date)),
				flt(record.working_hours),
			)
			for record in invalid_records[:10]
		]
	)

	if len(invalid_records) > 10:
		details += _(" and {0} more").format(len(invalid_records) - 10)

	frappe.throw(
		_(
			"Compensatory Leave Request requires attendance working hours to be greater than {0}. "
			"The following attendance date(s) do not qualify: {1}"
		).format(frappe.bold(min_working_hours), details)
	)


def get_min_working_hours(leave_type):
	if not frappe.get_meta("Leave Type").has_field(MIN_WORKING_HOURS_FIELD):
		return 0

	value = frappe.db.get_value("Leave Type", leave_type, MIN_WORKING_HOURS_FIELD)
	if value in (None, ""):
		return 6

	return flt(value)
