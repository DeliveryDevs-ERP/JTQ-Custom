import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	remove_unused_employee_group_field()
	create_custom_fields(
		{
			"Attendance": [
				{
					"fieldname": "custom_jtq_bulk_attendance",
					"fieldtype": "Link",
					"label": "JTQ Bulk Attendance",
					"options": "JTQ Bulk Attendance",
					"insert_after": "attendance_request",
					"read_only": 1,
					"no_copy": 1,
				},
				{
					"fieldname": "custom_jtq_bulk_attendance_row",
					"fieldtype": "Data",
					"label": "JTQ Bulk Attendance Row",
					"insert_after": "custom_jtq_bulk_attendance",
					"read_only": 1,
					"hidden": 1,
					"no_copy": 1,
				},
			],
			"Leave Application": [
				{
					"fieldname": "custom_jtq_bulk_attendance",
					"fieldtype": "Link",
					"label": "JTQ Bulk Attendance",
					"options": "JTQ Bulk Attendance",
					"insert_after": "description",
					"read_only": 1,
					"no_copy": 1,
				},
				{
					"fieldname": "custom_jtq_bulk_attendance_row",
					"fieldtype": "Data",
					"label": "JTQ Bulk Attendance Row",
					"insert_after": "custom_jtq_bulk_attendance",
					"read_only": 1,
					"hidden": 1,
					"no_copy": 1,
				},
			],
		},
		update=True,
	)

	if not frappe.db.exists("Report", "JTQ Bulk Attendance History"):
		return

	frappe.db.set_value("Report", "JTQ Bulk Attendance History", "disabled", 0)


def remove_unused_employee_group_field():
	fieldname = "Employee-custom_jtq_employee_group"
	if frappe.db.exists("Custom Field", fieldname):
		frappe.delete_doc("Custom Field", fieldname, force=1)
