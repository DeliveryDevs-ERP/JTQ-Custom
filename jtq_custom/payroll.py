import frappe
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils import add_months, cstr, flt, getdate


MEDICAL_ALLOWANCE_COMPONENT = "Medical Allowance"


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


@frappe.whitelist()
def get_employee_salary_structure_components(
	salary_structure,
	employee=None,
	assignment_from_date=None,
	date_of_joining=None,
):
	if not salary_structure:
		return {}

	salary_structure_doc = frappe.get_doc("Salary Structure", salary_structure)
	validate_salary_structure_for_employee_assignment(salary_structure_doc)
	earnings = get_employee_component_rows(salary_structure_doc.get("earnings"))
	if not is_medical_allowance_eligible(employee, assignment_from_date, date_of_joining):
		earnings = remove_medical_allowance_rows(earnings)

	return {
		"salary_structure": salary_structure_doc.name,
		"company": salary_structure_doc.company,
		"currency": salary_structure_doc.currency,
		"earnings": earnings,
		"deductions": get_employee_component_rows(salary_structure_doc.get("deductions")),
	}


def validate_salary_structure_for_employee_assignment(salary_structure_doc):
	if salary_structure_doc.docstatus != 1:
		frappe.throw(
			_("Salary Structure {0} must be submitted before assignment.").format(
				frappe.bold(salary_structure_doc.name)
			)
		)
	if salary_structure_doc.get("is_active") == "No":
		frappe.throw(
			_("Salary Structure {0} is inactive.").format(frappe.bold(salary_structure_doc.name))
		)


def get_employee_component_rows(rows):
	return [get_employee_component_row(row) for row in rows]


def get_employee_component_row(row):
	return {
		"salary_component": row.salary_component,
		"abbr": row.abbr,
		"amount": flt(row.amount),
		"depends_on_payment_days": row.depends_on_payment_days,
		"is_tax_applicable": row.is_tax_applicable,
		"condition": row.condition,
		"formula": row.formula,
		"amount_based_on_formula": row.amount_based_on_formula,
		"statistical_component": row.statistical_component,
		"is_flexible_benefit": row.is_flexible_benefit,
		"variable_based_on_taxable_salary": row.variable_based_on_taxable_salary,
		"exempted_from_income_tax": row.exempted_from_income_tax,
		"do_not_include_in_total": row.do_not_include_in_total,
		"do_not_include_in_accounts": row.do_not_include_in_accounts,
		"deduct_full_tax_on_selected_payroll_date": row.deduct_full_tax_on_selected_payroll_date,
	}


def is_medical_allowance_eligible(employee=None, assignment_from_date=None, date_of_joining=None):
	if employee and not date_of_joining:
		date_of_joining = frappe.db.get_value("Employee", employee, "date_of_joining")

	if not (date_of_joining and assignment_from_date):
		return False

	eligibility_date = add_months(getdate(date_of_joining), 6)
	return getdate(assignment_from_date) >= eligibility_date


def remove_medical_allowance_rows(rows):
	return [
		row
		for row in rows
		if not is_medical_allowance_component(row.get("salary_component"))
	]


def is_medical_allowance_component(salary_component):
	return cstr(salary_component).strip().lower() == MEDICAL_ALLOWANCE_COMPONENT.lower()


@frappe.whitelist()
def create_salary_assignment_from_employee(employee):
	if not employee:
		frappe.throw(_("Employee is required."))

	employee_doc = frappe.get_doc("Employee", employee)
	salary_structure = employee_doc.get("custom_salary_structure")
	from_date = employee_doc.get("custom_salary_assignment_from_date")

	if not salary_structure:
		frappe.throw(_("Please select Salary Structure in the Salary tab."))
	if not from_date:
		frappe.throw(_("Please select Assignment From Date in the Salary tab."))

	template = frappe.get_doc("Salary Structure", salary_structure)
	validate_salary_structure_for_employee_assignment(template)

	if employee_doc.company != template.company:
		frappe.throw(
			_("Selected Salary Structure belongs to {0}, but Employee belongs to {1}.").format(
				frappe.bold(template.company), frappe.bold(employee_doc.company)
			)
		)

	validate_employee_salary_components(employee_doc)
	cancel_latest_salary_structure_assignment(employee_doc.name)

	employee_salary_structure = create_employee_salary_structure(employee_doc, template, getdate(from_date))
	assignment = create_employee_salary_structure_assignment(
		employee_doc,
		employee_salary_structure,
		getdate(from_date),
	)

	employee_doc.db_set(
		"custom_current_salary_structure_assignment",
		assignment.name,
		update_modified=False,
	)

	frappe.msgprint(
		_("Salary Structure Assignment {0} created for Employee {1}.").format(
			frappe.bold(assignment.name), frappe.bold(employee_doc.name)
		),
		indicator="green",
	)

	return {
		"salary_structure": employee_salary_structure.name,
		"salary_structure_assignment": assignment.name,
	}


def validate_employee_salary_components(employee_doc):
	if not employee_doc.get("custom_employee_earnings"):
		frappe.throw(_("Please fetch or add Earning components before creating Salary Assignment."))

	for table_field, label in (
		("custom_employee_earnings", _("Earnings")),
		("custom_employee_deductions", _("Deductions")),
	):
		seen_components = set()
		for row in employee_doc.get(table_field):
			if not row.salary_component:
				frappe.throw(_("{0} row {1}: Salary Component is required.").format(label, row.idx))
			if row.salary_component in seen_components:
				frappe.throw(
					_("{0} row {1}: Duplicate Salary Component {2}.").format(
						label, row.idx, frappe.bold(row.salary_component)
					)
				)
			seen_components.add(row.salary_component)
			if flt(row.amount) < 0:
				frappe.throw(_("{0} row {1}: Amount cannot be negative.").format(label, row.idx))


def cancel_latest_salary_structure_assignment(employee):
	latest_assignment = frappe.db.get_value(
		"Salary Structure Assignment",
		{
			"employee": employee,
			"docstatus": 1,
		},
		"name",
		order_by="from_date desc, creation desc",
	)
	if not latest_assignment:
		return

	assignment = frappe.get_doc("Salary Structure Assignment", latest_assignment)
	assignment.flags.ignore_permissions = True
	assignment.cancel()


def create_employee_salary_structure(employee_doc, template, assignment_from_date):
	new_structure = frappe.new_doc("Salary Structure")
	new_structure.name = make_autoname(f"{employee_doc.name}-SS-.#####")
	new_structure.company = template.company
	new_structure.currency = template.currency
	new_structure.is_active = "Yes"
	new_structure.is_default = "No"
	new_structure.salary_slip_based_on_timesheet = template.get("salary_slip_based_on_timesheet")
	new_structure.payroll_frequency = template.get("payroll_frequency")
	new_structure.salary_component = template.get("salary_component")
	new_structure.hour_rate = template.get("hour_rate")
	new_structure.leave_encashment_amount_per_day = template.get("leave_encashment_amount_per_day")
	new_structure.max_benefits = template.get("max_benefits")
	new_structure.mode_of_payment = template.get("mode_of_payment")
	new_structure.payment_account = template.get("payment_account")

	for source_row in employee_doc.get("custom_employee_earnings"):
		if is_medical_allowance_component(source_row.salary_component) and not is_medical_allowance_eligible(
			employee_doc.name,
			assignment_from_date,
			employee_doc.date_of_joining,
		):
			continue
		append_salary_structure_component(new_structure, "earnings", source_row)
	for source_row in employee_doc.get("custom_employee_deductions"):
		append_salary_structure_component(new_structure, "deductions", source_row)

	new_structure.flags.ignore_permissions = True
	new_structure.insert()
	new_structure.submit()
	return new_structure


def append_salary_structure_component(salary_structure, table_field, source_row):
	row = salary_structure.append(table_field, {})
	row.salary_component = source_row.salary_component
	row.abbr = source_row.abbr
	row.amount = flt(source_row.amount)
	row.default_amount = flt(source_row.amount)
	row.additional_amount = 0
	row.condition = source_row.condition or ""
	row.formula = source_row.formula or ""
	row.amount_based_on_formula = source_row.amount_based_on_formula
	row.depends_on_payment_days = source_row.depends_on_payment_days
	row.is_tax_applicable = source_row.is_tax_applicable
	row.is_flexible_benefit = source_row.is_flexible_benefit
	row.variable_based_on_taxable_salary = source_row.variable_based_on_taxable_salary
	row.statistical_component = source_row.statistical_component
	row.exempted_from_income_tax = source_row.exempted_from_income_tax
	row.do_not_include_in_total = source_row.do_not_include_in_total
	row.do_not_include_in_accounts = source_row.do_not_include_in_accounts
	row.deduct_full_tax_on_selected_payroll_date = source_row.deduct_full_tax_on_selected_payroll_date
	row.custom_jtq_auto_populated = 1
	row.custom_jtq_amount_changed = 1


def create_employee_salary_structure_assignment(employee_doc, salary_structure, from_date):
	assignment = frappe.new_doc("Salary Structure Assignment")
	assignment.employee = employee_doc.name
	assignment.salary_structure = salary_structure.name
	assignment.company = employee_doc.company
	assignment.currency = salary_structure.currency
	assignment.from_date = from_date
	assignment.base = get_component_total(salary_structure.get("earnings"))
	assignment.variable = 0

	assignment.flags.ignore_permissions = True
	assignment.insert()
	assignment.submit()
	return assignment


def get_component_total(rows):
	return sum(flt(row.amount) for row in rows if not row.do_not_include_in_total)
