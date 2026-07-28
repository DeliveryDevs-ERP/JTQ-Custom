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
	},
});
