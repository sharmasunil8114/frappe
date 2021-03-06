# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import frappe
import frappe.defaults
from frappe.desk.notifications import delete_notification_count_for, clear_notifications

common_default_keys = ["__default", "__global"]

def clear_user_cache(user=None):
	cache = frappe.cache()

	groups = ("bootinfo", "user_recent", "roles", "user_doc", "lang",
		"defaults", "user_permissions", "home_page", "linked_with",
		"desktop_icons", 'portal_menu_items')

	if user:
		for name in groups:
			cache.hdel(name, user)
		cache.delete_keys("user:" + user)
		clear_defaults_cache(user)
	else:
		for name in groups:
			cache.delete_key(name)
		clear_global_cache()
		clear_defaults_cache()

	clear_notifications(user)

def clear_global_cache():
	clear_doctype_cache()
	frappe.cache().delete_value(["app_hooks", "installed_apps",
		"app_modules", "module_app", "notification_config", 'system_settings',
		'scheduler_events', 'time_zone', 'webhooks', 'active_domains', 'active_modules'])
	frappe.setup_module_map()

def clear_defaults_cache(user=None):
	if user:
		for p in ([user] + common_default_keys):
			frappe.cache().hdel("defaults", p)
	elif frappe.flags.in_install!="frappe":
		frappe.cache().delete_key("defaults")

def clear_doctype_cache(doctype=None):
	cache = frappe.cache()

	if getattr(frappe.local, 'meta_cache') and (doctype in frappe.local.meta_cache):
		del frappe.local.meta_cache[doctype]

	for key in ('is_table', 'doctype_modules'):
		cache.delete_value(key)

	groups = ["meta", "form_meta", "table_columns", "last_modified",
		"linked_doctypes", 'email_alerts', 'workflow']

	def clear_single(dt):
		for name in groups:
			cache.hdel(name, dt)

	if doctype:
		clear_single(doctype)

		# clear all parent doctypes
		for dt in frappe.db.sql("""select parent from tabDocField
			where fieldtype="Table" and options=%s""", (doctype,)):
			clear_single(dt[0])

		# clear all notifications
		delete_notification_count_for(doctype)

	else:
		# clear all
		for name in groups:
			cache.delete_value(name)

