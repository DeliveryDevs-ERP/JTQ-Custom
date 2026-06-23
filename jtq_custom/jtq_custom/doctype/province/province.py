from frappe.model.document import Document


class Province(Document):
	def validate(self):
		self.master_id = self.name
		if not self.title and self.province_name:
			self.title = self.province_name
		if not self.province_name and self.title:
			self.province_name = self.title
