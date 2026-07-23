from datetime import datetime, time, timedelta

import frappe
from frappe.utils import (
	add_to_date,
	date_diff,
	flt,
	get_datetime,
	get_time,
	getdate,
	time_diff_in_seconds,
)


def calculate_attendance_time_fields(doc, method=None):
	calculate_overtime_and_attendance_details(doc, method=method)


def calculate_overtime_and_attendance_details(doc, method=None):
	set_in_out_time_from_request(doc)
	reset_attendance_time_fields(doc)

	if not doc.employee or not doc.attendance_date:
		return

	shift_details = get_shift_details_for_attendance(doc)
	if not shift_details:
		return

	doc.custom_shift_hours = flt(shift_details.shift_hours, 2)

	if not (doc.get("in_time") and doc.get("out_time")):
		return

	in_time = get_datetime(doc.in_time)
	out_time = get_datetime(doc.out_time)
	working_hours = get_hour_difference(out_time, in_time)
	doc.working_hours = working_hours

	late_hours = get_hour_difference(in_time, shift_details.start_datetime)
	if late_hours:
		doc.custom_late_entry_hours = late_hours
		doc.custom_late_entry_detail = format_duration(late_hours)

	early_hours = get_hour_difference(shift_details.end_datetime, out_time)
	if early_hours:
		doc.custom_early_exit_hours = early_hours
		doc.custom_early_exit_detail = format_duration(early_hours)

	overtime_hours = max(working_hours - flt(shift_details.shift_hours), 0)
	if overtime_hours:
		doc.custom_overtime_hours = flt(overtime_hours, 2)
		doc.custom_overtime_detail = format_duration(overtime_hours)


def set_in_out_time_from_request(doc):
	if not doc.get("attendance_request"):
		return

	request = frappe.get_cached_doc("Attendance Request", doc.attendance_request)
	request_days = date_diff(request.to_date, request.from_date) + 1

	if request_days > 2:
		set_shift_in_out_time(doc)
		return

	in_seconds = time_to_seconds(request.get("custom_in_time"))
	out_seconds = time_to_seconds(request.get("custom_out_time"))
	set_in_out_time_from_seconds(doc, in_seconds, out_seconds)


def set_shift_in_out_time(doc):
	shift = doc.get("shift") or get_assigned_shift(doc.employee, doc.attendance_date)
	if not shift:
		return

	shift_times = frappe.db.get_value(
		"Shift Type",
		shift,
		["start_time", "end_time"],
		as_dict=True,
	)
	if not shift_times or not (shift_times.start_time and shift_times.end_time):
		return

	doc.shift = shift
	set_in_out_time_from_seconds(
		doc,
		time_to_seconds(shift_times.start_time),
		time_to_seconds(shift_times.end_time),
	)


def set_in_out_time_from_seconds(doc, in_seconds, out_seconds):
	day_start = get_datetime(getdate(doc.attendance_date))

	if in_seconds is not None:
		doc.in_time = add_to_date(day_start, seconds=in_seconds)

	if out_seconds is not None:
		out_time = add_to_date(day_start, seconds=out_seconds)
		if doc.get("in_time") and out_time <= get_datetime(doc.in_time):
			out_time = add_to_date(out_time, days=1)
		doc.out_time = out_time


def update_attendance_times_from_request(doc, method=None):
	attendance_names = frappe.get_all(
		"Attendance",
		filters={
			"attendance_request": doc.name,
			"docstatus": 1,
		},
		pluck="name",
	)

	for attendance_name in attendance_names:
		attendance = frappe.get_doc("Attendance", attendance_name)
		calculate_overtime_and_attendance_details(attendance)

		if not (attendance.get("in_time") and attendance.get("out_time")):
			continue

		frappe.db.set_value(
			"Attendance",
			attendance_name,
			{
				"in_time": attendance.in_time,
				"out_time": attendance.out_time,
				"working_hours": attendance.get("working_hours"),
				"late_entry": 0,
				"custom_shift_hours": attendance.get("custom_shift_hours"),
				"custom_late_entry_detail": attendance.get("custom_late_entry_detail"),
				"custom_late_entry_hours": attendance.get("custom_late_entry_hours"),
				"custom_early_exit_detail": attendance.get("custom_early_exit_detail"),
				"custom_early_exit_hours": attendance.get("custom_early_exit_hours"),
				"custom_overtime_detail": attendance.get("custom_overtime_detail"),
				"custom_overtime_hours": attendance.get("custom_overtime_hours"),
			},
			update_modified=False,
		)


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

	anchor_date = getdate(doc.in_time) if doc.get("in_time") else getdate(doc.attendance_date)
	start_datetime, end_datetime = get_shift_start_end_datetimes(
		anchor_date,
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


def time_to_seconds(value):
	if value in (None, ""):
		return None
	if isinstance(value, timedelta):
		return int(value.total_seconds())
	if isinstance(value, time):
		return value.hour * 3600 + value.minute * 60 + value.second

	parsed_time = normalize_time(value)
	return parsed_time.hour * 3600 + parsed_time.minute * 60 + parsed_time.second


def get_hour_difference(end_datetime, start_datetime):
	if not end_datetime or not start_datetime:
		return 0

	end_datetime = get_datetime(end_datetime)
	start_datetime = get_datetime(start_datetime)
	if end_datetime <= start_datetime:
		return 0

	return flt(time_diff_in_seconds(end_datetime, start_datetime) / 3600, 2)


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
