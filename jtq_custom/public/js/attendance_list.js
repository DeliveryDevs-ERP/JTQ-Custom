(function () {
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
