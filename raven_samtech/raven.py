# path : /home/frappe/frappe-bench/apps/raven/raven/raven_integrations/doctype/raven_document_notification/raven_document_notification.py
import frappe

def run_document_notification(doc, method):
	from raven.raven_integrations.doctype.raven_document_notification import raven_document_notification as rdn
	
	if doc.doctype in rdn.doctypes_to_be_ignored:
		return

	if (
		frappe.flags.in_import
		or frappe.flags.in_patch
		or frappe.flags.in_install
		or frappe.flags.in_uninstall
	):
		return

	def _get_notifications():
		"""Returns all enabled notifications for the document type"""
		notifications = frappe.get_all(
			"Raven Document Notification",
			filters={"document_type": doc.doctype, "enabled": 1},
			fields=["name", "send_alert_on", "condition", "custom_field_to_watch"],
		)
		return notifications

	raven_notifications = frappe.cache().hget(
		"raven_doc_notifications", doc.doctype, _get_notifications
	)

	if not raven_notifications:
		# No notifications found for the document type
		return

	event_map = {
		"on_update": "Update",
		"after_insert": "New Document",
		"on_submit": "Submit",
		"on_cancel": "Cancel",
		"on_trash": "Delete",
	}

	# TODO: Add value change event
	# if not doc.flags.in_insert or not doc.flags.in_delete:
	# 	# Value change is for update only
	# 	event_map["on_change"] = "Value Change"

	notifications_to_send = []

	for notification in raven_notifications:
		event = event_map.get(method, None)

		# Standard event handling
		if event and event == notification.send_alert_on and event != "Value Change":
			context = rdn.get_context(doc)
			if notification.condition:
				if not rdn.evaluate_condition(context, notification.condition, notification.name):
					continue
			notifications_to_send.append(notification)

		# Special handling for Value Change
		print("=======here=======", notification.custom_field_to_watch)
		if notification.send_alert_on == "Value Change" and notification.custom_field_to_watch and method == "on_update":
			field_to_watch = notification.custom_field_to_watch.split(" ")[0]
			print("=======123232=======", field_to_watch)
			if notification.custom_field_to_watch and doc.has_value_changed(field_to_watch):
				print("=======dddddddddddd=======", notification.custom_field_to_watch)
				context = rdn.get_context(doc)
				notifications_to_send.append(notification)

	if not notifications_to_send:
		return

	frappe.enqueue(
		rdn.send_raven_notifications,
		doc=doc,
		notifications_to_send=notifications_to_send,
		link_doctype=doc.doctype,
		link_document=doc.name,
		enqueue_after_commit=True,
	)