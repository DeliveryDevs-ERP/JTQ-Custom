import frappe
from frappe.utils import add_days, cint, flt, getdate

from hrms.hr.doctype.compensatory_leave_request.compensatory_leave_request import (
	CompensatoryLeaveRequest,
)


class JTQCompensatoryLeaveRequest(CompensatoryLeaveRequest):
	def validate(self):
		if self.work_from_date:
			self.work_end_date = self.work_from_date
		super().validate()

	def create_leave_allocation(self, leave_period, date_difference):
		is_carry_forward = frappe.db.get_value("Leave Type", self.leave_type, "is_carry_forward")
		allocation_from_date = add_days(self.work_end_date, 1)
		allocation = frappe.get_doc(
			dict(
				doctype="Leave Allocation",
				employee=self.employee,
				employee_name=self.employee_name,
				leave_type=self.leave_type,
				from_date=allocation_from_date,
				to_date=leave_period[0].to_date,
				carry_forward=cint(is_carry_forward),
				new_leaves_allocated=date_difference,
				total_leaves_allocated=date_difference,
				description=self.reason,
				custom_compensatory_leave_request=self.name,
			)
		)
		allocation.insert(ignore_permissions=True)
		allocation.submit()
		return allocation

	def on_cancel(self):
		linked_allocation = self.leave_allocation
		super().on_cancel()
		frappe.clear_messages()
		cancel_linked_compensatory_leave_allocation(self, linked_allocation)
		clear_compensatory_leave_allocation_link(self, linked_allocation)
		frappe.clear_messages()

	def on_trash(self):
		delete_linked_compensatory_leave_allocation(self)
		frappe.clear_messages()


def cancel_linked_compensatory_leave_allocation(doc, allocation_name=None):
	allocation_name = get_linked_compensatory_leave_allocation(doc, allocation_name)
	if not allocation_name:
		return

	allocation = frappe.get_doc("Leave Allocation", allocation_name)
	if allocation.docstatus != 1:
		return

	if has_linked_leave_applications(allocation.name):
		frappe.throw(
			frappe._(
				"Leave Allocation {0} cannot be cancelled because Leave Application records are linked to it."
			).format(frappe.bold(allocation.name))
		)

	allocation.flags.ignore_permissions = True
	allocation.cancel()
	frappe.clear_messages()


def delete_linked_compensatory_leave_allocation(doc):
	allocation_name = get_linked_compensatory_leave_allocation(doc)
	if not allocation_name:
		return

	allocation = frappe.get_doc("Leave Allocation", allocation_name)

	if has_linked_leave_applications(allocation.name):
		frappe.throw(
			frappe._(
				"Leave Allocation {0} cannot be deleted because Leave Application records are linked to it."
			).format(frappe.bold(allocation.name))
		)

	if allocation.docstatus == 1:
		allocation.flags.ignore_permissions = True
		allocation.cancel()
		allocation.reload()
		frappe.clear_messages()

	if allocation.docstatus == 2:
		allocation.flags.ignore_permissions = True
		allocation.delete()
		clear_compensatory_leave_allocation_link(doc, allocation_name)
		frappe.clear_messages()


def clear_compensatory_leave_allocation_link(doc, allocation_name=None):
	allocation_name = allocation_name or doc.get("leave_allocation")

	if allocation_name and frappe.db.exists("Leave Allocation", allocation_name):
		clear_leave_allocation_request_reference(allocation_name, doc.name)

	if doc.get("leave_allocation"):
		frappe.db.set_value(
			"Compensatory Leave Request",
			doc.name,
			"leave_allocation",
			None,
			update_modified=False,
		)
		doc.leave_allocation = None


def clear_leave_allocation_request_reference(allocation_name, compensatory_leave_request):
	if not frappe.get_meta("Leave Allocation").has_field("custom_compensatory_leave_request"):
		return

	if (
		frappe.db.get_value(
			"Leave Allocation",
			allocation_name,
			"custom_compensatory_leave_request",
		)
		== compensatory_leave_request
	):
		frappe.db.set_value(
			"Leave Allocation",
			allocation_name,
			"custom_compensatory_leave_request",
			None,
			update_modified=False,
		)


def clear_cancelled_compensatory_leave_allocation_links():
	for request in frappe.get_all(
		"Compensatory Leave Request",
		filters={
			"docstatus": 2,
			"leave_allocation": ["is", "set"],
		},
		fields=["name", "leave_allocation"],
	):
		doc = frappe.get_doc("Compensatory Leave Request", request.name)
		clear_compensatory_leave_allocation_link(doc, request.leave_allocation)

	frappe.db.commit()


def get_linked_compensatory_leave_allocation(doc, allocation_name=None):
	allocation_name = allocation_name or doc.get("leave_allocation")
	if allocation_name and is_allocation_created_by_request(allocation_name, doc.name):
		return allocation_name

	if allocation_name and is_zeroed_request_created_allocation(allocation_name, doc):
		return allocation_name

	return frappe.db.get_value(
		"Leave Allocation",
		{
			"custom_compensatory_leave_request": doc.name,
		},
		"name",
	)


def is_zeroed_request_created_allocation(leave_allocation, doc):
	allocation = frappe.db.get_value(
		"Leave Allocation",
		leave_allocation,
		[
			"employee",
			"leave_type",
			"from_date",
			"new_leaves_allocated",
			"total_leaves_allocated",
		],
		as_dict=True,
	)
	if not allocation:
		return False

	return (
		allocation.employee == doc.employee
		and allocation.leave_type == doc.leave_type
		and getdate(allocation.from_date) == getdate(add_days(doc.work_end_date, 1))
		and flt(allocation.new_leaves_allocated) <= 0
		and flt(allocation.total_leaves_allocated) <= 0
	)


def is_allocation_created_by_request(leave_allocation, compensatory_leave_request):
	return (
		frappe.db.get_value(
			"Leave Allocation",
			leave_allocation,
			"custom_compensatory_leave_request",
		)
		== compensatory_leave_request
	)


def has_linked_leave_applications(leave_allocation):
	allocation = frappe.db.get_value(
		"Leave Allocation",
		leave_allocation,
		["employee", "leave_type", "from_date", "to_date", "docstatus"],
		as_dict=True,
	)
	if not allocation or allocation.docstatus != 1:
		return False

	return frappe.db.exists(
		"Leave Application",
		{
			"employee": allocation.employee,
			"leave_type": allocation.leave_type,
			"docstatus": ["!=", 2],
			"from_date": ["<=", allocation.to_date],
			"to_date": [">=", allocation.from_date],
		},
	)
