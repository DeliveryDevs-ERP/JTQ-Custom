from frappe.model.document import Document


class Province(Document):
	def validate(self):
		self.master_id = self.name
