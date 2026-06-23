def set_master_id(doc, method=None):
	if doc.meta.has_field("master_id"):
		doc.master_id = doc.name
