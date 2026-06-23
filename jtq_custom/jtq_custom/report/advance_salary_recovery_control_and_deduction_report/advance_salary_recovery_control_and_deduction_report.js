frappe.query_reports["Advance Salary Recovery Control and Deduction Report"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "salary_component",
			label: __("Salary Component"),
			fieldtype: "Link",
			options: "Salary Component",
			get_query() {
				return {
					filters: {
						type: "Deduction",
					},
				};
			},
		},
		{
			fieldname: "status",
			label: __("Recovery Status"),
			fieldtype: "Select",
			options: "\nActive\nFully Recovered",
			default: "Active",
		},
	],
};
