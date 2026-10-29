"""Permissions enforcement — AWS-style AccessDenied for browser actions.

Uses core.iam.can() as the source of truth. Mirrors real AWS behavior:

  - Root user (or no current user) → implicit full access (unless an SCP denies)
  - IAM user → allowed only by explicit Allow in an attached policy
  - Default → deny

Real AWS also supports: explicit Deny wins, permission boundaries, SCPs,
session policies. MiniAWS simplifies to: root bypasses, everyone else is
checked via core.iam.can().
"""
import urllib.parse

from core import iam as iam_mod


def _current_identity():
    """Return 'root', 'None', or the logged-in username."""
    try:
        user = iam_mod.get_current_user()
    except Exception:
        return None
    return user


def is_root_session():
    """Root credentials (or no login) bypass all checks — matches real AWS."""
    user = _current_identity()
    return user is None or user == "root"


def check(action, resource="*"):
    """Return (allowed, error_message).

    If allowed is True, error_message is None.
    If allowed is False, error_message is a human-readable denial.
    """
    if is_root_session():
        return True, None

    user = _current_identity()

    try:
        result = iam_mod.can(action, resource)
    except Exception:
        # Conservative: if can() raises, deny.
        result = (False, "permission check raised")

    # core.iam.can() returns (bool, reason) — unwrap it.
    if isinstance(result, tuple):
        allowed = bool(result[0])
    else:
        allowed = bool(result)

    if allowed:
        return True, None

    # Build a real-AWS-shaped denial message
    msg = (
        f"User: arn:aws:iam::{{account}}:user/{user} is not authorized "
        f"to perform: {action} on resource: {resource}"
    )
    # Try to fill in account ID
    try:
        from core import account
        msg = msg.format(account=account.get_account_id() or "000000000000")
    except Exception:
        msg = msg.replace("{account}", "000000000000")

    return False, msg


def require(action, resource="*", back=None):
    """Convenience wrapper for action handlers.

    Returns:
      (True, None)              → caller proceeds
      (False, ('redirect', url)) → caller returns this directly
    """
    allowed, err = check(action, resource)
    if allowed:
        return True, None
    if back is None:
        back = "/"
    sep = "&" if "?" in back else "?"
    target = f"{back}{sep}error={urllib.parse.quote(err)}"
    return False, ("redirect", target)
