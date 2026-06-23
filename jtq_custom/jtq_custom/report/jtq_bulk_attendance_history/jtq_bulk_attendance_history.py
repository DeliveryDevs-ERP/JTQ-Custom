import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("JTQ Bulk Attendance"), "fieldname": "bulk_attendance", "fieldtype": "Link", "options": "JTQ Bulk Attendance", "width": 180},
		{"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 160},
		{"label": _("Date"), "fieldname": "attendance_date", "fieldtype": "Date", "width": 100},
		{"label": _("Action / Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Attendance Created"), "fieldname": "attendance", "fieldtype": "Link", "options": "Attendance", "width": 160},
		{"label": _("Leave Application Created"), "fieldname": "leave_application", "fieldtype": "Link", "options": "Leave Application", "width": 180},
		{"label": _("Shift"), "fieldname": "shift", "fieldtype": "Link", "options": "Shift Type", "width": 120},
	]


def get_data(filters):
	conditions = ["att.custom_jtq_bulk_attendance is not null", "att.docstatus != 2"]
	values = {}
	if filters.get("from_date"):
		conditions.append("att.attendance_date >= %(from_date)s")
		values["from_date"] = filters.from_date
	if filters.get("to_date"):
		conditions.append("att.attendance_date <= %(to_date)s")
		values["to_date"] = filters.to_date
	if filters.get("bulk_attendance"):
		conditions.append("att.custom_jtq_bulk_attendance = %(bulk_attendance)s")
		values["bulk_attendance"] = filters.bulk_attendance
	if filters.get("employee"):
		conditions.append("att.employee = %(employee)s")
		values["employee"] = filters.employee

	return frappe.db.sql(
		"""
		select
			att.custom_jtq_bulk_attendance as bulk_attendance,
			att.employee,
			att.employee_name,
			att.attendance_date,
			att.status,
			att.name as attendance,
			att.leave_application,
			att.shift
		from `tabAttendance` att
		where {conditions}
		order by att.attendance_date desc, att.employee_name
		""".format(conditions=" and ".join(conditions)),
		values,
		as_dict=True,
	)
