import frappe
from frappe.model.rename_doc import rename_doc


MASTER_DOCTYPES = {
	"City": {
		"app": "jtq_custom",
		"doctype": "city",
		"autoname_prefix": "City",
		"title_field": "title",
	},
	"Province": {
		"app": "jtq_custom",
		"doctype": "province",
		"autoname_prefix": "Province",
		"title_field": "title",
	},
	"Region": {
		"app": "donation_management",
		"doctype": "region",
		"autoname_prefix": "Region",
		"name_field": "region_name",
		"title_field": "region_name",
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
		normalize_doctype_display(doctype, details)
		rename_master_records(doctype, details.get("autoname_prefix"))
		backfill_master_records(doctype, details.get("name_field"))


def normalize_doctype_display(doctype, details):
	values = {
		"show_title_field_in_link": 1,
	}

	if details.get("title_field"):
		values["title_field"] = details["title_field"]
		values["search_fields"] = details["title_field"]

	if details.get("autoname_prefix"):
		values["autoname"] = f"{details['autoname_prefix']}-.#"
		values["naming_rule"] = "Expression"

	frappe.db.set_value("DocType", doctype, values, update_modified=False)


def rename_master_records(doctype, prefix):
	if not prefix:
		return

	records = frappe.get_all(doctype, fields=["name"], order_by="creation asc, name asc")
	used_names = {record.name for record in records if is_normalized_name(record.name, prefix)}
	counter = 1

	for record in records:
		if is_normalized_name(record.name, prefix):
			continue

		new_name, counter = get_next_master_name(doctype, prefix, used_names, counter)
		rename_doc(doctype, record.name, new_name, force=True, ignore_permissions=True)
		used_names.add(new_name)


def is_normalized_name(name, prefix):
	if not name.startswith(f"{prefix}-"):
		return False

	number_part = name.replace(f"{prefix}-", "", 1)
	return number_part.isdigit() and str(int(number_part)) == number_part


def get_next_master_name(doctype, prefix, used_names, counter):
	while True:
		new_name = f"{prefix}-{counter}"
		counter += 1
		if new_name in used_names:
			continue
		if frappe.db.exists(doctype, new_name):
			continue
		return new_name, counter


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
