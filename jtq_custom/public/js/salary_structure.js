frappe.ui.form.on("Salary Structure", {
	onload(frm) {
		populate_salary_structure_components(frm);
	},

	refresh(frm) {
		populate_salary_structure_components(frm);
	},
});

frappe.ui.form.on("Salary Detail", {
	amount(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.custom_jtq_auto_populated) {
			frappe.model.set_value(cdt, cdn, "custom_jtq_amount_changed", 1);
		}
	},
});

function populate_salary_structure_components(frm) {
	if (!frm.is_new() || frm.__jtq_populating_salary_components) {
		return;
	}

	if ((frm.doc.earnings || []).length || (frm.doc.deductions || []).length) {
		return;
	}

	frm.__jtq_populating_salary_components = true;
	frappe
		.call({
			method: "jtq_custom.payroll.get_salary_structure_components",
		})
		.then((response) => {
			const components = response.message || [];
			if ((frm.doc.earnings || []).length || (frm.doc.deductions || []).length) {
				return;
			}

			components.forEach((component) => {
				const table = component.type === "Earning" ? "earnings" : "deductions";
				const row = frm.add_child(table);
				row.salary_component = component.name;
				row.abbr = component.salary_component_abbr;
				row.amount = 0;
				row.default_amount = 0;
				row.additional_amount = 0;
				row.amount_based_on_formula = 0;
				row.formula = "";
				row.condition = "";
				row.depends_on_payment_days = component.depends_on_payment_days;
				row.is_tax_applicable = component.is_tax_applicable;
				row.is_flexible_benefit = component.is_flexible_benefit;
				row.variable_based_on_taxable_salary = component.variable_based_on_taxable_salary;
				row.statistical_component = component.statistical_component;
				row.exempted_from_income_tax = component.exempted_from_income_tax;
				row.do_not_include_in_total = component.do_not_include_in_total;
				row.do_not_include_in_accounts = component.do_not_include_in_accounts;
				row.deduct_full_tax_on_selected_payroll_date =
					component.deduct_full_tax_on_selected_payroll_date;
				row.custom_jtq_auto_populated = 1;
				row.custom_jtq_amount_changed = 0;
			});

			frm.refresh_field("earnings");
			frm.refresh_field("deductions");
		})
		.finally(() => {
			frm.__jtq_populating_salary_components = false;
		});
}
