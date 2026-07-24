frappe.ui.form.on("Attendance Request", {
	setup(frm) {
		frm.set_query("custom_attendance_request_approver", () => {
			const filters = { status: "Active" };
			if (frm.doc.company) {
				filters.company = frm.doc.company;
			}
			return { filters };
		});
	},
	validate(frm) {
		validate_future_dates(frm);
		toggle_time_fields(frm);
	},
	from_date(frm) {
		validate_future_dates(frm);
		toggle_time_fields(frm);
	},
	to_date(frm) {
		validate_future_dates(frm);
		toggle_time_fields(frm);
	},
	refresh(frm) {
		toggle_time_fields(frm);
	},
});

function validate_future_dates(frm) {
	const today = frappe.datetime.get_today();

	if (frm.doc.from_date && frm.doc.from_date > today) {
		frappe.throw(__("Future Attendance Request is not allowed."));
	}

	if (frm.doc.to_date && frm.doc.to_date > today) {
		frappe.throw(__("Future Attendance Request is not allowed."));
	}
}

function toggle_time_fields(frm) {
	let show = false;

	if (frm.doc.from_date && frm.doc.to_date) {
		const diff = frappe.datetime.get_day_diff(frm.doc.to_date, frm.doc.from_date);
		show = diff === 0 || diff === 1;
	}

	frm.toggle_display("custom_in_time", show);
	frm.toggle_display("custom_out_time", show);
	frm.toggle_reqd("custom_in_time", show);
	frm.toggle_reqd("custom_out_time", show);
}
