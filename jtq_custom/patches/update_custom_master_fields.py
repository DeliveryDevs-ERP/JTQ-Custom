import frappe


MASTER_DOCTYPES = {
	"City": {
		"app": "jtq_custom",
		"doctype": "city",
	},
	"Province": {
		"app": "jtq_custom",
		"doctype": "province",
	},
	"Region": {
		"app": "donation_management",
		"doctype": "region",
		"name_field": "region_name",
	},
	"Madrasa": {
		"app": "donation_management",
		"doctype": "madrasa",
		"name_field": "madrasa_name",
	},
}


def execute():
	for doctype, details in MASTER_DOCTYPES.items():
		if not frappe.db.exists("DocType", doctype):
			continue

		frappe.reload_doc(details["app"], "doctype", details["doctype"])
		backfill_master_records(doctype, details.get("name_field"))


def backfill_master_records(doctype, name_field):
	meta = frappe.get_meta(doctype)
	if not meta.has_field("master_id") or not meta.has_field("title"):
		return

	fields = ["name", "master_id", "title"]
	if name_field and meta.has_field(name_field):
		fields.append(name_field)

	for record in frappe.get_all(doctype, fields=fields):
		values = {
			"master_id": record.name,
			"title": record.title or record.get(name_field) or record.name,
		}
		if name_field and meta.has_field(name_field):
			values[name_field] = record.get(name_field) or record.title or record.name

		frappe.db.set_value(doctype, record.name, values, update_modified=False)
