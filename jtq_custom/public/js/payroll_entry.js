(function () {
	const jtq_filter_fields = [
		"custom_work_mode",
		"custom_city",
		"custom_province",
		"custom_country",
		"custom_region",
		"custom_madrasa",
	];

	frappe.ui.form.on("Payroll Entry", {
		setup(frm) {
			extend_employee_filters(frm);
		},
		refresh(frm) {
			extend_employee_filters(frm);
		},
	});

	function extend_employee_filters(frm) {
		if (!frm.events || frm.events.__jtq_filters_extended) {
			return;
		}

		const standard_get_employee_filters = frm.events.get_employee_filters;
		if (!standard_get_employee_filters) {
			return;
		}

		frm.events.get_employee_filters = function (frm) {
			const filters = standard_get_employee_filters.call(this, frm) || {};
			jtq_filter_fields.forEach((fieldname) => {
				if (frm.doc[fieldname] || frm.doc[fieldname] === 0) {
					filters[fieldname] = frm.doc[fieldname];
				}
			});
			return filters;
		};
		frm.events.__jtq_filters_extended = true;
	}
})();
