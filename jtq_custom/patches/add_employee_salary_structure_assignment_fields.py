from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(get_custom_fields(), update=True)


def get_custom_fields():
	return {
		"Employee": [
			{
				"fieldname": "custom_salary_structure",
				"fieldtype": "Link",
				"label": "Salary Structure",
				"options": "Salary Structure",
				"insert_after": "ctc",
			},
			{
				"fieldname": "custom_salary_assignment_from_date",
				"fieldtype": "Date",
				"label": "Assignment From Date",
				"insert_after": "custom_salary_structure",
			},
			{
				"fieldname": "custom_current_salary_structure_assignment",
				"fieldtype": "Link",
				"label": "Current Salary Structure Assignment",
				"options": "Salary Structure Assignment",
				"read_only": 1,
				"insert_after": "custom_salary_assignment_from_date",
			},
			{
				"fieldname": "custom_employee_salary_components_section",
				"fieldtype": "Section Break",
				"label": "Earnings and Deductions",
				"insert_after": "custom_current_salary_structure_assignment",
			},
			{
				"fieldname": "custom_employee_earnings",
				"fieldtype": "Table",
				"label": "Earnings",
				"options": "Employee Salary Component Detail",
				"insert_after": "custom_employee_salary_components_section",
			},
			{
				"fieldname": "custom_employee_deductions",
				"fieldtype": "Table",
				"label": "Deductions",
				"options": "Employee Salary Component Detail",
				"insert_after": "custom_employee_earnings",
			},
		]
	}
