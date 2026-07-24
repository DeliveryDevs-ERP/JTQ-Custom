import frappe
from frappe.model.document import Document


class EmployeeSalaryComponentDetail(Document):
	def validate(self):
		if self.amount and self.amount < 0:
			frappe.throw(
				frappe._("Row {0}: Amount cannot be negative.").format(self.idx or ""),
				title=frappe._("Invalid Amount"),
			)
