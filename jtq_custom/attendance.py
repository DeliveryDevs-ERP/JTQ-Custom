from datetime import datetime, time, timedelta

import frappe
from frappe.utils import flt, get_datetime, get_time, getdate


def calculate_attendance_time_fields(doc, method=None):
	reset_attendance_time_fields(doc)

	if not doc.employee or not doc.attendance_date:
		return

	shift_details = get_shift_details_for_attendance(doc)
	if not shift_details:
		return

	doc.custom_shift_hours = flt(shift_details.shift_hours, 2)

	if doc.get("late_entry"):
		late_hours = get_hour_difference(doc.get("in_time"), shift_details.start_datetime)
		doc.custom_late_entry_hours = late_hours
		doc.custom_late_entry_detail = format_duration(late_hours)

	if doc.get("early_exit"):
		early_hours = get_hour_difference(shift_details.end_datetime, doc.get("out_time"))
		doc.custom_early_exit_hours = early_hours
		doc.custom_early_exit_detail = format_duration(early_hours)

	working_hours = get_working_hours(doc)
	overtime_hours = max(working_hours - flt(shift_details.shift_hours), 0)
	if overtime_hours:
		doc.custom_overtime_hours = flt(overtime_hours, 2)
		doc.custom_overtime_detail = format_duration(overtime_hours)


def reset_attendance_time_fields(doc):
	for fieldname in (
		"custom_shift_hours",
		"custom_late_entry_hours",
		"custom_early_exit_hours",
		"custom_overtime_hours",
	):
		doc.set(fieldname, 0)

	for fieldname in (
		"custom_late_entry_detail",
		"custom_early_exit_detail",
		"custom_overtime_detail",
	):
		doc.set(fieldname, "")


def get_shift_details_for_attendance(doc):
	shift = doc.get("shift") or get_assigned_shift(doc.employee, doc.attendance_date)
	if not shift:
		return frappe._dict()

	shift_times = frappe.db.get_value(
		"Shift Type",
		shift,
		["start_time", "end_time"],
		as_dict=True,
	)
	if not shift_times:
		return frappe._dict()

	start_datetime, end_datetime = get_shift_start_end_datetimes(
		doc.attendance_date,
		shift_times.start_time,
		shift_times.end_time,
	)

	return frappe._dict(
		{
			"shift": shift,
			"start_datetime": start_datetime,
			"end_datetime": end_datetime,
			"shift_hours": get_hour_difference(end_datetime, start_datetime),
		}
	)


def get_assigned_shift(employee, attendance_date):
	shift = frappe.db.get_value(
		"Shift Assignment",
		{
			"employee": employee,
			"docstatus": 1,
			"status": "Active",
			"start_date": ["<=", attendance_date],
			"end_date": [">=", attendance_date],
		},
		"shift_type",
		order_by="start_date desc",
	)
	if shift:
		return shift

	shift = frappe.db.get_value(
		"Shift Assignment",
		{
			"employee": employee,
			"docstatus": 1,
			"status": "Active",
			"start_date": ["<=", attendance_date],
			"end_date": ["is", "not set"],
		},
		"shift_type",
		order_by="start_date desc",
	)
	if shift:
		return shift

	return frappe.db.get_value("Employee", employee, "default_shift")


def get_shift_start_end_datetimes(attendance_date, start_time, end_time):
	date = getdate(attendance_date)
	start_datetime = datetime.combine(date, normalize_time(start_time))
	end_datetime = datetime.combine(date, normalize_time(end_time))

	if end_datetime <= start_datetime:
		end_datetime += timedelta(days=1)

	return start_datetime, end_datetime


def normalize_time(value):
	if isinstance(value, timedelta):
		return (datetime.min + value).time()
	if isinstance(value, time):
		return value
	return get_time(value)


def get_working_hours(doc):
	if flt(doc.get("working_hours")):
		return flt(doc.working_hours)

	if doc.get("in_time") and doc.get("out_time"):
		return get_hour_difference(doc.out_time, doc.in_time)

	return 0


def get_hour_difference(end_datetime, start_datetime):
	if not end_datetime or not start_datetime:
		return 0

	end_datetime = get_datetime(end_datetime)
	start_datetime = get_datetime(start_datetime)
	if end_datetime <= start_datetime:
		return 0

	return flt((end_datetime - start_datetime).total_seconds() / 3600, 2)


def format_duration(hours):
	total_minutes = round(flt(hours) * 60)
	if total_minutes <= 0:
		return ""

	duration_hours = total_minutes // 60
	duration_minutes = total_minutes % 60
	parts = []

	if duration_hours:
		parts.append(f"{duration_hours} {'Hour' if duration_hours == 1 else 'Hours'}")
	if duration_minutes:
		parts.append(f"{duration_minutes} {'Min' if duration_minutes == 1 else 'Mins'}")

	return " ".join(parts)
