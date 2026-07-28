frappe.ui.form.on("Compensatory Leave Request", {
	setup(frm) {
		frm.ignore_doctypes_on_cancel_all = [
			"Leave Allocation",
			"Leave Ledger Entry",
		];
	},
	refresh(frm) {
		frm.ignore_doctypes_on_cancel_all = [
			"Leave Allocation",
			"Leave Ledger Entry",
		];
		set_single_work_date(frm);
	},
	work_from_date(frm) {
		set_single_work_date(frm);
	},
});

function set_single_work_date(frm) {
	if (frm.doc.work_from_date && frm.doc.work_end_date !== frm.doc.work_from_date) {
		frm.set_value("work_end_date", frm.doc.work_from_date);
	}
}
