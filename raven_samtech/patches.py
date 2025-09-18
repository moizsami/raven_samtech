# raven_samtech/patches.py
import frappe

def patch_raven_run():
  
    try:
        from raven.raven_integrations.doctype.raven_document_notification import raven_document_notification as rdn
    except Exception as e:
        frappe.log_error(f"raven_samtech: Raven module not found / import failed: {e}", "raven_samtech.patch_raven_run")
        return

    try:
        from raven_samtech.raven import run_document_notification as custom_run
    except Exception as e:
        frappe.log_error(f"raven_samtech: custom run_document_notification import failed: {e}", "raven_samtech.patch_raven_run")
        return

    
    try:
        rdn.run_document_notification = custom_run
        frappe.logger().info("raven_samtech: Patched Raven run_document_notification()")
    except Exception as e:
        frappe.log_error(f"raven_samtech: failed to patch function: {e}", "raven_samtech.patch_raven_run")
