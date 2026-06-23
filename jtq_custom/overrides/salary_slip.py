import frappe
from frappe.utils import flt

from hrms.payroll.doctype.salary_slip.salary_slip import (
	SalarySlip,
	get_salary_component_data,
)

from jtq_custom.payroll import get_month_count


class JTQSalarySlip(SalarySlip):
	def add_additional_salary_components(self, component_type):
		super().add_additional_salary_components(component_type)

		if component_type == "deductions":
			self.apply_advance_recovery_controls()

	def apply_advance_recovery_controls(self):
		for additional_salary in get_active_advance_recoveries(
			self.employee, self.start_date, self.end_date
		):
			principal_amount = get_principal_amount(additional_salary)
			total_recovered = get_total_recovered_amount(additional_salary.name, exclude_salary_slip=self.name)
			pending_amount = max(principal_amount - total_recovered, 0)

			if not pending_amount:
				remove_additional_salary_row(self, additional_salary.name)
				continue

			deduction_amount = min(flt(additional_salary.amount), pending_amount)
			if not deduction_amount and additional_salary.get("custom_paused"):
				remove_additional_salary_row(self, additional_salary.name)
				continue

			component_data = get_salary_component_data(additional_salary.salary_component)
			self.update_component_row(
				component_data,
				deduction_amount,
				"deductions",
				frappe._dict(
					{
						"name": additional_salary.name,
						"overwrite": additional_salary.overwrite_salary_structure_amount,
						"is_recurring": additional_salary.is_recurring,
						"deduct_full_tax_on_selected_payroll_date": additional_salary.deduct_full_tax_on_selected_payroll_date,
					}
				),
				is_recurring=additional_salary.is_recurring,
			)


def get_active_advance_recoveries(employee, start_date, end_date):
	return frappe.get_all(
		"Additional Salary",
		filters={
			"employee": employee,
			"docstatus": 1,
			"type": "Deduction",
			"is_recurring": 1,
			"disabled": 0,
			"custom_adjustment_type": "Advance Recovery",
			"from_date": ["<=", end_date],
		},
		fields=[
			"name",
			"employee",
			"salary_component",
			"amount",
			"is_recurring",
			"from_date",
			"to_date",
			"overwrite_salary_structure_amount",
			"deduct_full_tax_on_selected_payroll_date",
			"custom_total_adjustment_amount",
			"custom_paused",
		],
	)


def get_principal_amount(additional_salary):
	return flt(additional_salary.custom_total_adjustment_amount) or (
		flt(additional_salary.amount)
		* get_month_count(additional_salary.from_date, additional_salary.to_date)
	)


def get_total_recovered_amount(additional_salary, exclude_salary_slip=None):
	conditions = [
		"ded.parenttype = 'Salary Slip'",
		"ded.parentfield = 'deductions'",
		"ded.additional_salary = %(additional_salary)s",
		"sal.docstatus = 1",
	]
	values = {"additional_salary": additional_salary}
	if exclude_salary_slip:
		conditions.append("ded.parent != %(exclude_salary_slip)s")
		values["exclude_salary_slip"] = exclude_salary_slip

	return flt(
		frappe.db.sql(
			"""
			select sum(ded.amount)
			from `tabSalary Detail` ded
			inner join `tabSalary Slip` sal on sal.name = ded.parent
			where {conditions}
			""".format(conditions=" and ".join(conditions)),
			values,
		)
		[0][0]
	)


def remove_additional_salary_row(salary_slip, additional_salary):
	rows = [
		row
		for row in salary_slip.get("deductions")
		if row.additional_salary != additional_salary
	]
	salary_slip.set("deductions", rows)
