import frappe
from frappe.utils import cstr

from hrms.payroll.doctype.salary_structure.salary_structure import SalaryStructure

from jtq_custom.payroll import populate_salary_structure_components


class JTQSalaryStructure(SalaryStructure):
	def before_validate(self):
		populate_salary_structure_components(self)
		super().before_validate()

	def set_missing_values(self):
		overwritten_fields = [
			"depends_on_payment_days",
			"variable_based_on_taxable_salary",
			"is_tax_applicable",
			"is_flexible_benefit",
		]
		overwritten_fields_if_missing = ["amount_based_on_formula", "formula", "amount"]

		for table in ["earnings", "deductions"]:
			for row in self.get(table):
				component_default_value = frappe.db.get_value(
					"Salary Component",
					cstr(row.salary_component),
					overwritten_fields + overwritten_fields_if_missing,
					as_dict=1,
				)
				if not component_default_value:
					continue

				for fieldname in overwritten_fields:
					value = component_default_value.get(fieldname)
					if row.get(fieldname) != value:
						row.set(fieldname, value)

				if row.get("custom_jtq_auto_populated"):
					row.amount_based_on_formula = 0
					row.formula = ""
					row.amount = row.amount or 0
					continue

				if not (row.get("amount") or row.get("formula")):
					for fieldname in overwritten_fields_if_missing:
						row.set(fieldname, component_default_value.get(fieldname))
