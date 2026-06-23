import frappe
from frappe import _
from frappe.utils import cint, flt

from hrms.hr.report.employee_leave_balance import employee_leave_balance as standard_report

Filters = frappe._dict


def execute(filters: Filters | None = None) -> tuple:
	filters = frappe._dict(filters or {})

	if filters.to_date <= filters.from_date:
		frappe.throw(_('"From Date" can not be greater than or equal to "To Date"'))

	columns = standard_report.get_columns()
	data = get_data(filters)
	charts = standard_report.get_chart_data(data, filters)
	return columns, data, None, charts


def get_data(filters: Filters) -> list:
	leave_types = standard_report.get_leave_types()
	active_employees = get_employees(filters)

	precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
	consolidate_leave_types = len(active_employees) > 1 and filters.consolidate_leave_types

	data = []

	for leave_type in leave_types:
		if consolidate_leave_types:
			data.append({"leave_type": leave_type})

		for employee in active_employees:
			row = frappe._dict({} if consolidate_leave_types else {"leave_type": leave_type})
			row.employee = employee.name
			row.employee_name = employee.employee_name

			leaves_taken = (
				standard_report.get_leaves_for_period(
					employee.name, leave_type, filters.from_date, filters.to_date
				)
				* -1
			)

			new_allocation, expired_leaves, carry_forwarded_leaves = (
				standard_report.get_allocated_and_expired_leaves(
					filters.from_date, filters.to_date, employee.name, leave_type
				)
			)
			opening = standard_report.get_opening_balance(
				employee.name, leave_type, filters, carry_forwarded_leaves
			)

			row.leaves_allocated = flt(new_allocation, precision)
			row.leaves_expired = flt(expired_leaves, precision)
			row.opening_balance = flt(opening, precision)
			row.leaves_taken = flt(leaves_taken, precision)

			closing = new_allocation + opening - (row.leaves_expired + leaves_taken)
			row.closing_balance = flt(closing, precision)
			row.indent = 1
			data.append(row)

	return data


def get_employees(filters: Filters) -> list[dict]:
	Employee = frappe.qb.DocType("Employee")
	query = frappe.qb.from_(Employee).select(
		Employee.name,
		Employee.employee_name,
		Employee.department,
	)

	for field in ["company", "department"]:
		if filters.get(field):
			query = query.where(getattr(Employee, field) == filters.get(field))

	custom_filter_map = {
		"city": "custom_city",
		"province": "custom_province",
		"country": "custom_country",
		"work_mode": "custom_work_mode",
	}
	employee_meta = frappe.get_meta("Employee")
	for filter_name, employee_field in custom_filter_map.items():
		if filters.get(filter_name) and employee_meta.has_field(employee_field):
			query = query.where(getattr(Employee, employee_field) == filters.get(filter_name))

	if filters.get("employee"):
		query = query.where(Employee.name == filters.get("employee"))

	if filters.get("employee_status"):
		query = query.where(Employee.status == filters.get("employee_status"))

	return query.run(as_dict=True)
