import os

import frappe
from frappe.utils import flt, formatdate, getdate, today


BASIC_SALARY_COMPONENTS = {"basic", "basic salary"}
MEDICAL_ALLOWANCE_COMPONENT = "medical allowance"
OTHER_ALLOWANCE_COMPONENT = "other allowance"


def get_employee_appointment_context(employee):
	if not employee:
		return frappe._dict()

	doc = frappe.get_doc("Employee", employee) if isinstance(employee, str) else employee
	reference_date = doc.get("date_of_joining") or today()
	salary = get_employee_salary_components(doc.name)
	shift_location = get_employee_shift_location(doc.name, reference_date)

	basic_salary = salary.get("basic_salary", 0)
	medical_allowance = salary.get("medical_allowance", 0)
	other_allowance = salary.get("other_allowance", 0)

	employment_type = doc.get("employment_type") or doc.get("custom_employment_type")

	return frappe._dict(
		employee=doc.name,
		employee_name=doc.get("employee_name") or doc.name,
		father_name=doc.get("custom_father_name") or doc.get("father_name") or "",
		current_address=doc.get("current_address") or "",
		permanent_address=doc.get("permanent_address") or doc.get("current_address") or "",
		branch=get_link_display("Branch", doc.get("branch")),
		employment_type=get_link_display("Employment Type", employment_type),
		shift_location=get_link_display("Shift Location", shift_location),
		designation=get_link_display("Designation", doc.get("designation")),
		department=get_link_display("Department", doc.get("department")),
		date_of_joining=formatdate(reference_date, "dd/MM/yyyy") if reference_date else "",
		cnic=doc.get("cnic") or doc.get("passport_number") or "",
		phone=doc.get("cell_number") or doc.get("personal_phone") or "",
		bank_account=doc.get("bank_ac_no") or "",
		bank_name=doc.get("bank_name") or "",
		basic_salary=basic_salary,
		medical_allowance=medical_allowance,
		other_allowance=other_allowance,
		total_salary=basic_salary + medical_allowance + other_allowance,
		signature_image=get_manager_signature_image(),
	)


def get_employee_salary_components(employee):
	values = frappe._dict(basic_salary=0, medical_allowance=0, other_allowance=0)
	rows = frappe.get_all(
		"Employee Salary Component Detail",
		filters={
			"parent": employee,
			"parenttype": "Employee",
			"parentfield": "custom_employee_earnings",
		},
		fields=["salary_component", "amount"],
		limit_page_length=100,
	)

	for row in rows:
		component = (row.salary_component or "").strip().lower()
		amount = flt(row.amount)
		if component in BASIC_SALARY_COMPONENTS or "basic" in component:
			values.basic_salary = amount
		elif component == MEDICAL_ALLOWANCE_COMPONENT:
			values.medical_allowance = amount
		elif component == OTHER_ALLOWANCE_COMPONENT:
			values.other_allowance = amount

	return values


def get_employee_shift_location(employee, reference_date):
	reference_date = getdate(reference_date or today())
	assignment = frappe.db.sql(
		"""
		select shift_location
		from `tabShift Assignment`
		where employee = %s
			and docstatus < 2
			and status = 'Active'
			and start_date <= %s
			and (end_date is null or end_date >= %s)
		order by start_date desc, modified desc
		limit 1
		""",
		(employee, reference_date, reference_date),
		as_dict=True,
	)
	if assignment:
		return assignment[0].shift_location

	assignment = frappe.get_all(
		"Shift Assignment",
		filters={"employee": employee, "docstatus": ["<", 2], "status": "Active"},
		fields=["shift_location"],
		order_by="start_date desc, modified desc",
		limit_page_length=1,
	)
	return assignment[0].shift_location if assignment else ""


def get_link_display(doctype, value):
	if not value:
		return ""

	try:
		meta = frappe.get_meta(doctype)
	except Exception:
		return value

	title_field = meta.get("title_field")
	if title_field:
		return frappe.db.get_value(doctype, value, title_field) or value

	return value


def get_manager_signature_image():
	image_path = frappe.get_app_path("jtq_custom", "public", "img", "manager_hr_signature.png")
	if os.path.exists(image_path):
		return "/assets/jtq_custom/img/manager_hr_signature.png"

	return ""
