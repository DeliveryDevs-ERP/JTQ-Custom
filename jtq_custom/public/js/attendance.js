frappe.ui.form.on("Attendance", {
	refresh(frm) {
		ensure_jtq_attendance_indicator_styles();
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
	frm.dashboard.set_headline_alert(`<span class="jtq-attendance-source ${source.css_class}">${__(source.label)}</span>`);
}

function get_present_source(doc) {
	if (doc.custom_jtq_bulk_attendance) {
		return {
			label: "Present",
			css_class: "jtq-present-bulk",
		};
	}

	if (doc.attendance_request) {
		return {
			label: "Present",
			css_class: "jtq-present-request",
		};
	}

	return {
		label: "Present",
		css_class: "jtq-present-standard",
	};
}

function ensure_jtq_attendance_indicator_styles() {
	if (document.getElementById("jtq-attendance-indicator-styles")) {
		return;
	}

	const style = document.createElement("style");
	style.id = "jtq-attendance-indicator-styles";
	style.textContent = `
		.jtq-attendance-source {
			display: inline-flex;
			align-items: center;
			gap: 6px;
			font-weight: 600;
		}
		.jtq-attendance-source::before {
			content: "";
			width: 8px;
			height: 8px;
			border-radius: 50%;
			background: var(--indicator-dot-green);
		}
		.jtq-attendance-source.jtq-present-bulk::before {
			background: #f6dc8a;
		}
		.jtq-attendance-source.jtq-present-request::before {
			background: #a3effe;
		}
	`;
	document.head.appendChild(style);
}
