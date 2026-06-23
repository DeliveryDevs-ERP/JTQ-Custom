frappe.query_reports["JTQ Bulk Attendance History"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "bulk_attendance",
			label: __("JTQ Bulk Attendance"),
			fieldtype: "Link",
			options: "JTQ Bulk Attendance",
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
	],
};
