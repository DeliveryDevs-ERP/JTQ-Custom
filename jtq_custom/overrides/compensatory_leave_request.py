import frappe
from frappe.utils import add_days, cint, flt, getdate

from hrms.hr.doctype.compensatory_leave_request.compensatory_leave_request import (
	CompensatoryLeaveRequest,
)


class JTQCompensatoryLeaveRequest(CompensatoryLeaveRequest):
	def create_leave_allocation(self, leave_period, date_difference):
		is_carry_forward = frappe.db.get_value("Leave Type", self.leave_type, "is_carry_forward")
		allocation = frappe.get_doc(
			dict(
				doctype="Leave Allocation",
				employee=self.employee,
				employee_name=self.employee_name,
				leave_type=self.leave_type,
				from_date=add_days(self.work_end_date, 1),
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
		super().on_cancel()
		frappe.clear_messages()
		cancel_linked_compensatory_leave_allocation(self)
		frappe.clear_messages()

	def on_trash(self):
		delete_linked_compensatory_leave_allocation(self)
		frappe.clear_messages()


def cancel_linked_compensatory_leave_allocation(doc):
	allocation_name = get_linked_compensatory_leave_allocation(doc)
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
		frappe.clear_messages()


def get_linked_compensatory_leave_allocation(doc):
	if doc.get("leave_allocation") and is_allocation_created_by_request(doc.leave_allocation, doc.name):
		return doc.leave_allocation

	if doc.get("leave_allocation") and is_zeroed_request_created_allocation(doc.leave_allocation, doc):
		return doc.leave_allocation

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
