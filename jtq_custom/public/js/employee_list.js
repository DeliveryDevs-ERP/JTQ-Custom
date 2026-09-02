(function () {
  const completion_event = "jtq_bulk_salary_assignments_completed";
  const existing_settings = frappe.listview_settings["Employee"] || {};
  const existing_onload = existing_settings.onload;

  frappe.listview_settings["Employee"] = {
    ...existing_settings,
    onload(list_view) {
      if (existing_onload) {
        existing_onload.call(this, list_view);
      }

      list_view.page.add_actions_menu_item(
        __("Create Salary Structure Assignments"),
        () => create_bulk_salary_assignments(list_view)
      );
      register_completion_listener(completion_event);
    },
  };
})();

function create_bulk_salary_assignments(list_view) {
  const employees = list_view
    .get_checked_items()
    .map((employee) => employee.name);
  if (!employees.length) {
    frappe.msgprint(__("Please select at least one Employee."));
    return;
  }

  frappe.confirm(
    __("Create Salary Structure Assignments for {0} selected Employee(s)?", [
      employees.length,
    ]),
    () => {
      frappe
        .call({
          method:
            "jtq_custom.payroll.bulk_create_salary_assignments_from_employees",
          args: { employees },
          freeze: true,
          freeze_message: __("Creating Salary Structure Assignments..."),
        })
        .then((response) => {
          const result = response.message || {};
          if (result.queued) {
            frappe.show_alert({
              message: __(
                "Salary Structure Assignments have been queued for {0} Employees.",
                [result.total]
              ),
              indicator: "blue",
            });
            return;
          }

          show_bulk_salary_assignment_result(result);
          list_view.refresh();
        });
    }
  );
}

function register_completion_listener(completion_event) {
  if (window.jtq_bulk_salary_assignment_listener_registered) {
    return;
  }

  frappe.realtime.on(completion_event, (result) => {
    show_bulk_salary_assignment_result(result || {});
    if (window.cur_list && window.cur_list.doctype === "Employee") {
      window.cur_list.refresh();
    }
  });
  window.jtq_bulk_salary_assignment_listener_registered = true;
}

function show_bulk_salary_assignment_result(result) {
  const successful = result.success || [];
  const failed = result.failed || [];
  const sections = [
    `<p>${__("Created {0} of {1} Salary Structure Assignment(s).", [
      successful.length,
      result.total || successful.length + failed.length,
    ])}</p>`,
  ];

  if (successful.length) {
    const links = successful.map((row) => {
      const employee = frappe.utils.escape_html(row.employee || "");
      const assignment = frappe.utils.get_form_link(
        "Salary Structure Assignment",
        row.salary_structure_assignment,
        true
      );
      return `<li>${employee}: ${assignment}</li>`;
    });
    sections.push(
      `<p><strong>${__("Successful")}</strong></p><ul>${links.join("")}</ul>`
    );
  }

  if (failed.length) {
    const failures = failed.map((row) => {
      const employee = frappe.utils.escape_html(row.employee || "");
      const message = frappe.utils.escape_html(
        row.message || __("Unknown error")
      );
      return `<li>${employee}: ${message}</li>`;
    });
    sections.push(
      `<p><strong>${__("Failed")}</strong></p><ul>${failures.join("")}</ul>`
    );
  }

  frappe.msgprint({
    title: __("Salary Structure Assignment Results"),
    message: `<div style="max-height: 420px; overflow-y: auto;">${sections.join(
      ""
    )}</div>`,
    indicator: failed.length ? "orange" : "green",
  });
}
