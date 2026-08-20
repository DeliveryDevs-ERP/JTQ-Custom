frappe.ui.form.on("Salary Slip", {
	employee(frm) {
		set_assigned_salary_structure(frm);
	},

	start_date(frm) {
		set_assigned_salary_structure(frm);
	},

	end_date(frm) {
		set_assigned_salary_structure(frm);
	},

	payroll_frequency(frm) {
		set_assigned_salary_structure(frm);
	},
});

function set_assigned_salary_structure(frm) {
	if (frm.doc.docstatus !== 0 || !frm.doc.employee) {
		return;
	}

	if (!(frm.doc.start_date || frm.doc.end_date)) {
		return;
	}

	frappe.call({
		method: "jtq_custom.overrides.salary_slip.get_assigned_salary_structure",
		args: {
			employee: frm.doc.employee,
			start_date: frm.doc.start_date,
			end_date: frm.doc.end_date,
			payroll_frequency: frm.doc.payroll_frequency,
			salary_slip_based_on_timesheet: frm.doc.salary_slip_based_on_timesheet,
		},
		callback(response) {
			const assignment = response.message;
			if (assignment && assignment.salary_structure) {
				frm.set_value("salary_structure", assignment.salary_structure);
			}
		},
	});
}
