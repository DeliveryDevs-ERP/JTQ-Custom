import frappe


MASTER_DOCTYPES = {
	"City": {
		"app": "jtq_custom",
		"doctype": "city",
		"name_field": "city_name",
	},
	"Province": {
		"app": "jtq_custom",
		"doctype": "province",
		"name_field": "province_name",
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
		backfill_master_records(doctype, details["name_field"])


def backfill_master_records(doctype, name_field):
	meta = frappe.get_meta(doctype)
	if not meta.has_field("master_id") or not meta.has_field("title") or not meta.has_field(name_field):
		return

	for record in frappe.get_all(doctype, fields=["name", "master_id", "title", name_field]):
		title = record.title or record.get(name_field) or record.name
		display_name = record.get(name_field) or record.title or record.name
		frappe.db.set_value(
			doctype,
			record.name,
			{
				"master_id": record.name,
				"title": title,
				name_field: display_name,
			},
			update_modified=False,
		)
