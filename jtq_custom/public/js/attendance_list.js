(function () {
	ensure_jtq_attendance_indicator_styles();

	const existing_settings = frappe.listview_settings["Attendance"] || {};
	const existing_onload = existing_settings.onload;

	frappe.listview_settings["Attendance"] = {
		...existing_settings,
		add_fields: get_attendance_add_fields(existing_settings.add_fields),

		get_indicator(doc) {
			if (doc.status === "Present") {
				const source = get_present_source(doc);
				return [__(source.label), source.color, "status,=,Present"];
			}

			if (doc.status === "Work From Home") {
				return [__(doc.status), "green", `status,=,${doc.status}`];
			}

			if (["Absent", "On Leave"].includes(doc.status)) {
				return [__(doc.status), "red", `status,=,${doc.status}`];
			}

			if (doc.status === "Half Day") {
				return [__(doc.status), "orange", `status,=,${doc.status}`];
			}
		},

		onload(list_view) {
			if (existing_onload) {
				existing_onload.call(this, list_view);
			}
		},
	};
})();

function get_attendance_add_fields(existing_fields) {
	const fields = existing_fields || [];
	return [
		...new Set([
			...fields,
			"status",
			"attendance_date",
			"attendance_request",
			"custom_jtq_bulk_attendance",
		]),
	];
}

function get_present_source(doc) {
	if (doc.custom_jtq_bulk_attendance) {
		return {
			label: "Present",
			color: "jtq-present-bulk",
		};
	}

	if (doc.attendance_request) {
		return {
			label: "Present",
			color: "jtq-present-request",
		};
	}

	return {
		label: "Present",
		color: "green",
	};
}

function ensure_jtq_attendance_indicator_styles() {
	if (document.getElementById("jtq-attendance-indicator-styles")) {
		return;
	}

	const style = document.createElement("style");
	style.id = "jtq-attendance-indicator-styles";
	style.textContent = `
		.indicator-pill.jtq-present-bulk {
			background: #F5C527;
			color: #1f2933;
		}
		.indicator-pill.jtq-present-request {
			background: #64DDF5;
			color: #1f2933;
		}
	`;
	document.head.appendChild(style);
}
