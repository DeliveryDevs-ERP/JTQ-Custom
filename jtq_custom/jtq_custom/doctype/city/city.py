# Copyright (c) 2026, JTQ and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class City(Document):
	def validate(self):
		self.master_id = self.name
