frappe.ui.form.on("Employee", {
	setup(frm) {
		frm.set_query("custom_salary_structure", () => {
			const filters = {
				docstatus: 1,
				is_active: "Yes",
			};
			if (frm.doc.company) {
				filters.company = frm.doc.company;
			}
			return { filters };
		});
	},

	refresh(frm) {
		toggle_salary_assignment_button(frm);
	},

	company(frm) {
		if (frm.doc.custom_salary_structure) {
			frm.set_value("custom_salary_structure", "");
			clear_employee_salary_components(frm);
		}
	},

	date_of_joining(frm) {
		refetch_salary_components_if_ready(frm);
	},

	custom_salary_structure(frm) {
		if (!frm.doc.custom_salary_structure) {
			clear_employee_salary_components(frm);
			return;
		}

		if (!frm.doc.custom_salary_assignment_from_date) {
			frm.set_value("custom_salary_assignment_from_date", frappe.datetime.get_today());
		}

		fetch_salary_structure_components(frm);
	},

	custom_salary_assignment_from_date(frm) {
		refetch_salary_components_if_ready(frm);
		toggle_salary_assignment_button(frm);
	},
});

frappe.ui.form.on("Employee Salary Component Detail", {
	amount(frm) {
		toggle_salary_assignment_button(frm);
	},
});

function toggle_salary_assignment_button(frm) {
	if (frm.is_new() || !frm.doc.custom_salary_structure || !frm.doc.custom_salary_assignment_from_date) {
		return;
	}

	frm.add_custom_button(__("Salary Assignment"), () => {
		create_salary_assignment(frm);
	});
}

function fetch_salary_structure_components(frm) {
	frappe.call({
		method: "jtq_custom.payroll.get_employee_salary_structure_components",
		args: {
			salary_structure: frm.doc.custom_salary_structure,
			employee: frm.doc.name,
			assignment_from_date: frm.doc.custom_salary_assignment_from_date,
			date_of_joining: frm.doc.date_of_joining,
		},
		callback(response) {
			const data = response.message || {};
			fill_component_table(frm, "custom_employee_earnings", data.earnings || []);
			fill_component_table(frm, "custom_employee_deductions", data.deductions || []);
			frm.refresh_field("custom_employee_earnings");
			frm.refresh_field("custom_employee_deductions");
			toggle_salary_assignment_button(frm);
		},
	});
}

function refetch_salary_components_if_ready(frm) {
	if (frm.doc.custom_salary_structure && frm.doc.custom_salary_assignment_from_date) {
		fetch_salary_structure_components(frm);
	}
}

function fill_component_table(frm, table_field, rows) {
	frm.clear_table(table_field);
	rows.forEach((source) => {
		const row = frm.add_child(table_field);
		Object.assign(row, {
			salary_component: source.salary_component,
			abbr: source.abbr,
			amount: source.amount || 0,
			depends_on_payment_days: source.depends_on_payment_days,
			is_tax_applicable: source.is_tax_applicable,
			condition: source.condition,
			formula: source.formula,
			amount_based_on_formula: source.amount_based_on_formula,
			statistical_component: source.statistical_component,
			is_flexible_benefit: source.is_flexible_benefit,
			variable_based_on_taxable_salary: source.variable_based_on_taxable_salary,
			exempted_from_income_tax: source.exempted_from_income_tax,
			do_not_include_in_total: source.do_not_include_in_total,
			do_not_include_in_accounts: source.do_not_include_in_accounts,
			deduct_full_tax_on_selected_payroll_date: source.deduct_full_tax_on_selected_payroll_date,
		});
	});
}

function clear_employee_salary_components(frm) {
	frm.clear_table("custom_employee_earnings");
	frm.clear_table("custom_employee_deductions");
	frm.refresh_field("custom_employee_earnings");
	frm.refresh_field("custom_employee_deductions");
}

function create_salary_assignment(frm) {
	const run = () => {
		frappe.call({
			method: "jtq_custom.payroll.create_salary_assignment_from_employee",
			args: {
				employee: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Creating Salary Assignment..."),
			callback(response) {
				const data = response.message || {};
				if (data.salary_structure_assignment) {
					frm.set_value(
						"custom_current_salary_structure_assignment",
						data.salary_structure_assignment
					);
					frm.reload_doc();
				}
			},
		});
	};

	if (frm.is_dirty()) {
		frm.save().then(run);
	} else {
		run();
	}
}
