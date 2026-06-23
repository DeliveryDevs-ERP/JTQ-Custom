frappe.ui.form.on("Attendance", {
	refresh(frm) {
		show_present_source_indicator(frm);
	},
	status(frm) {
		show_present_source_indicator(frm);
	},
	attendance_request(frm) {
		show_present_source_indicator(frm);
	},
	custom_jtq_bulk_attendance(frm) {
		show_present_source_indicator(frm);
	},
});

function show_present_source_indicator(frm) {
	if (!frm.dashboard) {
		return;
	}

	frm.dashboard.clear_headline();

	if (frm.doc.status !== "Present") {
		return;
	}

	const source = get_present_source(frm.doc);
	frm.dashboard.set_headline_alert(
		`<span class="indicator ${source.color}">${__(source.label)}</span>`,
		source.color
	);
}

function get_present_source(doc) {
	if (doc.custom_jtq_bulk_attendance) {
		return {
			label: "Present",
			color: "blue",
		};
	}

	if (doc.attendance_request) {
		return {
			label: "Present - Request Approved",
			color: "orange",
		};
	}

	return {
		label: "Present - Standard",
		color: "green",
	};
}
