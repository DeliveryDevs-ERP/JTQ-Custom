import frappe
from frappe import _

from hrms.payroll.doctype.payroll_entry.payroll_entry import (
	PayrollEntry,
	get_employee_list,
)


class JTQPayrollEntry(PayrollEntry):
	def make_filters(self):
		filters = super().make_filters()
		for fieldname in get_jtq_payroll_filter_fields():
			filters[fieldname] = self.get(fieldname)
		return filters

	@frappe.whitelist()
	def fill_employee_details(self):
		filters = self.make_filters()
		employees = get_employee_list(filters=filters, as_dict=True, ignore_match_conditions=True)
		employees = self.filter_employees_by_jtq_fields(employees)
		self.set("employees", [])

		if not employees:
			frappe.throw(self.get_no_employees_message(), title=_("No employees found"))

		self.set("employees", employees)
		self.number_of_employees = len(self.employees)
		self.update_employees_with_withheld_salaries()

		return self.get_employees_with_unmarked_attendance()

	def filter_employees_by_jtq_fields(self, employees):
		if not employees or not self.has_jtq_payroll_filters():
			return employees

		employee_names = [employee.employee for employee in employees]
		employee_filters = {"name": ["in", employee_names]}
		employee_meta = frappe.get_meta("Employee")

		for payroll_field, employee_field in get_jtq_payroll_filter_map().items():
			value = self.get(payroll_field)
			if value and employee_meta.has_field(employee_field):
				employee_filters[employee_field] = value

		if len(employee_filters) == 1:
			return employees

		matching_employees = set(frappe.get_all("Employee", filters=employee_filters, pluck="name"))
		return [employee for employee in employees if employee.employee in matching_employees]

	def has_jtq_payroll_filters(self):
		return any(self.get(fieldname) for fieldname in get_jtq_payroll_filter_fields())

	def get_no_employees_message(self):
		message = _(
			"No employees found for the mentioned criteria:<br>Company: {0}<br> Currency: {1}<br>Payroll Payable Account: {2}"
		).format(
			frappe.bold(self.company),
			frappe.bold(self.currency),
			frappe.bold(self.payroll_payable_account),
		)

		standard_filters = {
			"branch": _("Branch"),
			"department": _("Department"),
			"designation": _("Designation"),
			"start_date": _("Start date"),
			"end_date": _("End date"),
		}
		for fieldname, label in standard_filters.items():
			if self.get(fieldname):
				message += "<br>" + _("{0}: {1}").format(label, frappe.bold(self.get(fieldname)))

		for fieldname, label in get_jtq_payroll_filter_labels().items():
			if self.get(fieldname):
				message += "<br>" + _("{0}: {1}").format(label, frappe.bold(self.get(fieldname)))

		return message


def get_jtq_payroll_filter_map():
	return {
		"custom_work_mode": "custom_work_mode",
		"custom_city": "custom_city",
		"custom_country": "custom_country",
		"custom_province": "custom_province",
		"custom_madrasa": "custom_madrasa",
	}


def get_jtq_payroll_filter_fields():
	return tuple(get_jtq_payroll_filter_map())


def get_jtq_payroll_filter_labels():
	return {
		"custom_work_mode": _("Work Mode"),
		"custom_city": _("City"),
		"custom_country": _("Country"),
		"custom_province": _("Province"),
		"custom_madrasa": _("Madrasa"),
	}
