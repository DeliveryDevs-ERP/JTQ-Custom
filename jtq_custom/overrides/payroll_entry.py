import frappe
from frappe import _

from hrms.payroll.doctype.payroll_entry.payroll_entry import (
	PayrollEntry,
	get_employee_list,
)


class JTQPayrollEntry(PayrollEntry):
	def make_filters(self):
		return super().make_filters()

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

		matching_employees = set(get_matching_employees(employee_filters, self))
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
		"custom_region": "custom_region",
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
		"custom_region": _("Region"),
		"custom_madrasa": _("Madrasa"),
	}


def get_matching_employees(employee_filters, payroll_entry):
	exact_matches = set(frappe.get_all("Employee", filters=employee_filters, pluck="name"))
	legacy_matches = get_legacy_title_matches(employee_filters, payroll_entry)
	return exact_matches | legacy_matches


def get_legacy_title_matches(employee_filters, payroll_entry):
	conditions = ["name in %(employees)s"]
	values = {"employees": employee_filters["name"][1]}

	for payroll_field, employee_field in get_jtq_payroll_filter_map().items():
		value = payroll_entry.get(payroll_field)
		if not value:
			continue

		candidates = get_filter_value_candidates(payroll_field, value)
		if not candidates:
			candidates = [value]

		conditions.append(f"`{employee_field}` in %({employee_field})s")
		values[employee_field] = tuple(candidates)

	return set(
		frappe.db.sql(
			f"""
			select name
			from `tabEmployee`
			where {" and ".join(conditions)}
			""",
			values,
			pluck=True,
		)
	)


def get_filter_value_candidates(payroll_field, value):
	link_doctype = {
		"custom_work_mode": "Work Mode",
		"custom_city": "City",
		"custom_province": "Province",
		"custom_region": "Region",
		"custom_madrasa": "Madrasa",
	}.get(payroll_field)

	if not link_doctype:
		return [value]

	candidates = [value]
	meta = frappe.get_meta(link_doctype)
	for fieldname in ("title", "work_mode", "region_name", "madrasa_name", "province_name", "city_name"):
		if meta.has_field(fieldname):
			title = frappe.db.get_value(link_doctype, value, fieldname)
			if title and title not in candidates:
				candidates.append(title)

	return candidates


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def employee_query(doctype, txt, searchfield, start, page_len, filters):
	filters = frappe._dict(filters)

	if not filters.payroll_frequency:
		frappe.throw(_("Select Payroll Frequency."))

	employee_list = get_employee_list(
		filters,
		searchfield=searchfield,
		search_string=txt,
		fields=["name", "employee_name"],
		as_dict=False,
		limit=page_len,
		offset=start,
	)

	if not has_jtq_filters(filters):
		return employee_list

	employee_names = [employee[0] for employee in employee_list]
	if not employee_names:
		return employee_list

	employee_filters = {"name": ["in", employee_names]}
	matching_employees = get_matching_employees(employee_filters, filters)

	return [employee for employee in employee_list if employee[0] in matching_employees]


def has_jtq_filters(filters):
	return any(filters.get(fieldname) not in (None, "") for fieldname in get_jtq_payroll_filter_fields())
