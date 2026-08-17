import json
from urllib.error import URLError
from urllib.request import urlopen

import frappe
from frappe.utils import getdate


ALADHAN_GREGORIAN_TO_HIJRI_URL = "https://api.aladhan.com/v1/gToH/{date}"


def set_employee_hijri_date(doc, method=None):
	"""Populate Employee custom_hijri_date from date_of_joining."""
	if not doc.get("date_of_joining"):
		doc.custom_hijri_date = None
		return

	if not should_fetch_hijri_date(doc):
		return

	hijri_date = get_hijri_date_from_gregorian(doc.date_of_joining)
	if hijri_date:
		doc.custom_hijri_date = hijri_date


def should_fetch_hijri_date(doc):
	if doc.is_new():
		return True

	if not doc.get("custom_hijri_date"):
		return True

	try:
		old_doc = doc.get_doc_before_save()
	except Exception:
		old_doc = None

	if old_doc and old_doc.get("date_of_joining") != doc.get("date_of_joining"):
		return True

	return False


@frappe.whitelist()
def get_hijri_date_from_gregorian(gregorian_date):
	if not gregorian_date:
		return None

	date = getdate(gregorian_date)
	cache_key = date.isoformat()
	cached_date = frappe.cache().hget("jtq_custom:hijri_dates", cache_key)
	if cached_date:
		return cached_date

	api_date = date.strftime("%d-%m-%Y")
	url = ALADHAN_GREGORIAN_TO_HIJRI_URL.format(date=api_date)

	try:
		with urlopen(url, timeout=8) as response:
			payload = json.loads(response.read().decode("utf-8"))
	except (TimeoutError, URLError, OSError, json.JSONDecodeError) as exc:
		frappe.log_error(
			title="Hijri Date Fetch Failed",
			message=f"Unable to fetch Hijri date for {api_date}: {exc}",
		)
		return None

	hijri_date = (((payload or {}).get("data") or {}).get("hijri") or {}).get("date")
	if not hijri_date:
		frappe.log_error(
			title="Hijri Date Fetch Failed",
			message=f"AlAdhan response did not include Hijri date for {api_date}: {payload}",
		)
		return None

	parsed_hijri_date = parse_aladhan_hijri_date(hijri_date)
	frappe.cache().hset("jtq_custom:hijri_dates", cache_key, parsed_hijri_date)
	return parsed_hijri_date


def parse_aladhan_hijri_date(hijri_date):
	day, month, year = hijri_date.split("-")
	return f"{year}-{month}-{day}"
