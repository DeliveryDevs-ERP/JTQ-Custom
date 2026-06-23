import frappe
from frappe import _
from frappe.utils import flt, formatdate

from jtq_custom.payroll import get_month_count


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{
			"label": _("Additional Salary"),
			"fieldname": "additional_salary",
			"fieldtype": "Link",
			"options": "Additional Salary",
			"width": 180,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 130,
		},
		{"label": _("Employee Name"), "fieldname": "employee_name", "width": 180},
		{
			"label": _("Salary Component"),
			"fieldname": "salary_component",
			"fieldtype": "Link",
			"options": "Salary Component",
			"width": 170,
		},
		{
			"label": _("Total Advance Given"),
			"fieldname": "total_advance_given",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": _("Total Recovered Amount"),
			"fieldname": "total_recovered_amount",
			"fieldtype": "Currency",
			"width": 170,
		},
		{
			"label": _("Total Pending to Recover"),
			"fieldname": "total_pending_to_recover",
			"fieldtype": "Currency",
			"width": 180,
		},
		{
			"label": _("Total Installments"),
			"fieldname": "total_installments",
			"fieldtype": "Int",
			"width": 140,
		},
		{
			"label": _("Installments Paid"),
			"fieldname": "installments_paid",
			"fieldtype": "Int",
			"width": 140,
		},
		{
			"label": _("Current Installment Amount"),
			"fieldname": "current_installment_amount",
			"fieldtype": "Currency",
			"width": 180,
		},
		{"label": _("From Date"), "fieldname": "from_date", "fieldtype": "Date", "width": 110},
		{"label": _("To Date"), "fieldname": "to_date", "fieldtype": "Date", "width": 110},
		{"label": _("Status"), "fieldname": "status", "width": 120},
	]


def get_data(filters):
	additional_salaries = get_advance_recovery_additional_salaries(filters)
	if not additional_salaries:
		return []

	recovery_map = get_recovery_map([row.name for row in additional_salaries])
	data = []

	for row in additional_salaries:
		total_installments = get_month_count(row.from_date, row.to_date)
		total_advance_given = flt(row.custom_total_adjustment_amount) or (
			flt(row.amount) * total_installments
		)
		recovery = recovery_map.get(row.name, frappe._dict())
		total_recovered = flt(recovery.get("recovered_amount"))
		pending = max(total_advance_given - total_recovered, 0)
		status = _("Fully Recovered") if total_advance_given and pending <= 0 else _("Active")

		if filters.get("status") and status != filters.status:
			continue

		data.append(
			{
				"additional_salary": row.name,
				"employee": row.employee,
				"employee_name": row.employee_name,
				"salary_component": row.salary_component,
				"total_advance_given": total_advance_given,
				"total_recovered_amount": total_recovered,
				"total_pending_to_recover": pending,
				"total_installments": total_installments,
				"installments_paid": int(recovery.get("installments_paid") or 0),
				"current_installment_amount": row.amount,
				"from_date": row.from_date,
				"to_date": row.to_date,
				"status": status,
			}
		)

	return data


def get_advance_recovery_additional_salaries(filters):
	conditions = [
		"ads.docstatus = 1",
		"ads.type = 'Deduction'",
		"ads.is_recurring = 1",
		"ads.custom_adjustment_type = 'Advance Recovery'",
	]
	values = {}

	if filters.get("company"):
		conditions.append("ads.company = %(company)s")
		values["company"] = filters.company
	if filters.get("employee"):
		conditions.append("ads.employee = %(employee)s")
		values["employee"] = filters.employee
	if filters.get("salary_component"):
		conditions.append("ads.salary_component = %(salary_component)s")
		values["salary_component"] = filters.salary_component

	return frappe.db.sql(
		"""
		select
			ads.name,
			ads.employee,
			ads.employee_name,
			ads.salary_component,
			ads.amount,
			ads.from_date,
			ads.to_date,
			ads.custom_total_adjustment_amount
		from `tabAdditional Salary` ads
		where {conditions}
		order by ads.employee_name, ads.from_date
		""".format(conditions=" and ".join(conditions)),
		values,
		as_dict=True,
	)


def get_recovery_map(additional_salaries):
	recovery_rows = frappe.db.sql(
		"""
		select
			ded.additional_salary,
			sum(ded.amount) as recovered_amount,
			count(distinct ded.parent) as installments_paid
		from `tabSalary Detail` ded
		inner join `tabSalary Slip` sal on sal.name = ded.parent
		where ded.parenttype = 'Salary Slip'
			and ded.parentfield = 'deductions'
			and ded.additional_salary in %(additional_salaries)s
			and sal.docstatus = 1
			and ded.amount > 0
		group by ded.additional_salary
		""",
		{"additional_salaries": tuple(additional_salaries)},
		as_dict=True,
	)

	return {row.additional_salary: row for row in recovery_rows}
