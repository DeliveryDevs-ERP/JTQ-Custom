frappe.ui.form.on("JTQ Bulk Attendance", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Get Employees"), () => {
				fetch_employees(frm, true);
			});
		}

		if (frm.doc.docstatus === 1 && ["Failed", "Partial"].includes(frm.doc.processing_status)) {
			frm.add_custom_button(__("Retry Processing"), () => {
				queue_attendance_processing(frm);
			});
		}
	},
	from_date: refetch_on_filter_change,
	to_date: refetch_on_filter_change,
	shift: refetch_on_filter_change,
	company: refetch_on_filter_change,
	branch: refetch_on_filter_change,
	employee_group: refetch_on_filter_change,
	department: refetch_on_filter_change,
	employment_type: refetch_on_filter_change,
	designation: refetch_on_filter_change,
	employee_grade: refetch_on_filter_change,
});

function process_attendance(frm) {
	if (frm.is_new()) {
		frappe.msgprint(__("Please save the document before processing attendance."));
		return;
	}

	if (frm.is_dirty()) {
		frm.save().then(() => queue_attendance_processing(frm));
		return;
	}

	queue_attendance_processing(frm);
}

function queue_attendance_processing(frm) {
	frappe.call({
		method: "jtq_custom.jtq_custom.doctype.jtq_bulk_attendance.jtq_bulk_attendance.process_attendance",
		args: {
			docname: frm.doc.name,
		},
		freeze: true,
		freeze_message: __("Queuing Attendance Processing..."),
		callback(response) {
			const result = response.message || {};
			frappe.msgprint(
				__("Attendance processing has been queued. Current status: {0}", [
					result.processing_status || __("Queued"),
				])
			);
			frm.reload_doc();
		},
	});
}

function refetch_on_filter_change(frm) {
	if (frm.__bulk_attendance_fetching) {
		return;
	}

	clear_employee_rows(frm);
}

function clear_employee_rows(frm) {
	frm.clear_table("employees");
	frm.set_value("total_employees", 0);
	frm.set_value("processed_count", 0);
	frm.set_value("failed_count", 0);
	frm.set_value("processing_status", "Draft");
	frm.refresh_field("employees");
}

function fetch_employees(frm, show_message) {
	if (frm.is_new()) {
		frappe.msgprint(__("Please save the document before fetching employees."));
		return;
	}

	if (!frm.doc.company) {
		frappe.msgprint(__("Please select Company before fetching employees."));
		return;
	}

	if (!frm.doc.from_date || !frm.doc.to_date) {
		frappe.msgprint(__("Please select From Date and To Date before fetching employees."));
		return;
	}

	if (frm.is_dirty()) {
		frm.save().then(() => fetch_employees(frm, show_message));
		return;
	}

	frm.__bulk_attendance_fetching = true;
	frappe.call({
		method: "jtq_custom.jtq_custom.doctype.jtq_bulk_attendance.jtq_bulk_attendance.get_employees",
		args: {
			docname: frm.doc.name,
		},
		freeze: true,
		freeze_message: __("Fetching Employees..."),
	})
		.then(async (response) => {
			const result = response.message || {};
			if (show_message) {
				frappe.msgprint(__("{0} employees loaded.", [result.total_employees || 0]));
			}
			await frm.reload_doc();
			frm.refresh_field("employees");
		})
		.finally(() => {
			frm.__bulk_attendance_fetching = false;
		});
}
