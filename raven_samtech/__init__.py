__version__ = "0.0.1"
# raven_samtech/__init__.py
from .patches import patch_raven_run

# Try to patch immediately on import so all workers get it.
try:
    patch_raven_run()
except Exception:
    # Don't crash app import; errors are already logged in the patcher.
    pass
