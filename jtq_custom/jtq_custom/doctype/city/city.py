# Copyright (c) 2026, JTQ and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class City(Document):
	def validate(self):
		self.master_id = self.name
		if not self.title and self.city_name:
			self.title = self.city_name
		if not self.city_name and self.title:
			self.city_name = self.title
