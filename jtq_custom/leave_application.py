import frappe
from frappe import _
from frappe.utils import cint, get_link_to_form


MIN_CONSECUTIVE_LEAVES_FIELD = "custom_min_consecutive_leaves_allowed"


def validate_leave_type_minimum_consecutive_leaves(doc, method=None):
	min_days = cint(doc.get(MIN_CONSECUTIVE_LEAVES_FIELD))
	max_days = cint(doc.get("max_continuous_days_allowed"))

	if min_days and max_days and min_days > max_days:
		frappe.throw(
			_("Minimum Consecutive Leaves Allowed cannot be greater than Maximum Consecutive Leaves Allowed.")
		)


def validate_minimum_consecutive_leaves(doc, method=None):
	if not doc.employee or not doc.leave_type or not doc.from_date or not doc.to_date:
		return

	if doc.status not in ("Open", "Approved"):
		return

	if not frappe.get_meta("Leave Type").has_field(MIN_CONSECUTIVE_LEAVES_FIELD):
		return

	min_days = cint(frappe.db.get_value("Leave Type", doc.leave_type, MIN_CONSECUTIVE_LEAVES_FIELD))
	if not min_days:
		return

	details = doc.get_consecutive_leave_details()
	if details.total_consecutive_leaves >= min_days:
		return

	msg = _("Leave of type {0} cannot be shorter than {1} consecutive day(s).").format(
		get_link_to_form("Leave Type", doc.leave_type),
		min_days,
	)
	if details.leave_applications:
		msg += "<br><br>" + _("Reference: {0}").format(
			", ".join(get_link_to_form("Leave Application", name) for name in details.leave_applications)
		)

	frappe.throw(msg, title=_("Minimum Consecutive Leaves Required"))
