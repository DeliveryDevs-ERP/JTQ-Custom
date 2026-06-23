import frappe
from frappe import _
from frappe.utils import flt


def sync_additional_salary_controls(doc, method=None):
	if doc.get("custom_adjustment_type") == "Overtime":
		hours = flt(doc.get("custom_overtime_hours"))
		rate = flt(doc.get("custom_overtime_rate"))
		if hours and rate:
			doc.amount = hours * rate

	if doc.get("custom_paused"):
		doc.disabled = 1
	elif doc.get("custom_paused") == 0:
		doc.disabled = 0

	total_amount = flt(doc.get("custom_total_adjustment_amount"))
	if not total_amount:
		total_amount = get_default_total_amount(doc)

	doc.custom_total_adjustment_amount = total_amount
	doc.custom_paid_or_deducted_amount = flt(doc.get("custom_paid_or_deducted_amount"))
	doc.custom_remaining_balance = max(total_amount - doc.custom_paid_or_deducted_amount, 0)


def sync_advance_recovery_from_salary_slip(doc, method=None):
	additional_salaries = {
		row.additional_salary
		for row in doc.get("deductions", [])
		if row.additional_salary
	}

	for additional_salary in additional_salaries:
		sync_advance_recovery_balance(additional_salary)


def sync_advance_recovery_balance(additional_salary):
	import frappe

	doc = frappe.get_doc("Additional Salary", additional_salary)
	if doc.get("custom_adjustment_type") != "Advance Recovery":
		return

	recovered_amount = get_recovered_amount(additional_salary)
	total_amount = flt(doc.get("custom_total_adjustment_amount")) or get_default_total_amount(doc)
	doc.db_set(
		{
			"custom_total_adjustment_amount": total_amount,
			"custom_paid_or_deducted_amount": recovered_amount,
			"custom_remaining_balance": max(total_amount - recovered_amount, 0),
			"disabled": 1 if total_amount and recovered_amount >= total_amount else doc.disabled,
		},
		update_modified=False,
	)


def get_recovered_amount(additional_salary):
	import frappe

	return flt(
		frappe.db.sql(
			"""
			select sum(ded.amount)
			from `tabSalary Detail` ded
			inner join `tabSalary Slip` sal on sal.name = ded.parent
			where ded.parenttype = 'Salary Slip'
				and ded.parentfield = 'deductions'
				and ded.additional_salary = %(additional_salary)s
				and sal.docstatus = 1
			""",
			{"additional_salary": additional_salary},
		)[0][0]
	)


def get_default_total_amount(doc):
	if doc.get("is_recurring") and doc.get("from_date") and doc.get("to_date"):
		return flt(doc.amount) * get_month_count(doc.from_date, doc.to_date)
	return flt(doc.amount)


def get_month_count(from_date, to_date):
	from frappe.utils import getdate

	start_date = getdate(from_date)
	end_date = getdate(to_date)
	if end_date < start_date:
		return 0

	return ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month) + 1


def populate_salary_structure_components(doc, method=None):
	if not doc.get("earnings"):
		add_salary_component_rows(doc, "earnings", "Earning")
	if not doc.get("deductions"):
		add_salary_component_rows(doc, "deductions", "Deduction")


def add_salary_component_rows(doc, table_field, component_type):
	for component in get_salary_structure_components(component_type):
		row = doc.append(table_field, {})
		set_salary_detail_from_component(row, component)


@frappe.whitelist()
def get_salary_structure_components(component_type=None):
	filters = {"disabled": 0}
	if component_type:
		filters["type"] = component_type

	return frappe.get_all(
		"Salary Component",
		filters=filters,
		fields=[
			"name",
			"salary_component_abbr",
			"type",
			"depends_on_payment_days",
			"is_tax_applicable",
			"is_flexible_benefit",
			"variable_based_on_taxable_salary",
			"statistical_component",
			"exempted_from_income_tax",
			"do_not_include_in_total",
			"do_not_include_in_accounts",
			"deduct_full_tax_on_selected_payroll_date",
		],
		order_by="type asc, name asc",
	)


def set_salary_detail_from_component(row, component):
	row.salary_component = component.name
	row.abbr = component.salary_component_abbr
	row.amount = 0
	row.default_amount = 0
	row.additional_amount = 0
	row.amount_based_on_formula = 0
	row.formula = ""
	row.condition = ""
	row.depends_on_payment_days = component.depends_on_payment_days
	row.is_tax_applicable = component.is_tax_applicable
	row.is_flexible_benefit = component.is_flexible_benefit
	row.variable_based_on_taxable_salary = component.variable_based_on_taxable_salary
	row.statistical_component = component.statistical_component
	row.exempted_from_income_tax = component.exempted_from_income_tax
	row.do_not_include_in_total = component.do_not_include_in_total
	row.do_not_include_in_accounts = component.do_not_include_in_accounts
	row.deduct_full_tax_on_selected_payroll_date = component.deduct_full_tax_on_selected_payroll_date
	row.custom_jtq_auto_populated = 1
	row.custom_jtq_amount_changed = 0
