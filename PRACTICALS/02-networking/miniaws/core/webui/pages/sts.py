"""STS pages — get-caller-identity 'who am I' page."""
import html

from core import account
from core import iam as iam_mod


def _esc(s):
    return html.escape(str(s))


def render_get_caller_identity(qs=None):
    """The STS console's only real page — who am I, in what account."""
    s = account.summary()
    account_id = s.get("account_id") or "(not initialized)"
    current_user = None
    try:
        current_user = iam_mod.get_current_user()
    except Exception:
        current_user = None

    # Treat "root" or any falsy value as unauthenticated root creds (matches AWS).
    is_root = not current_user or str(current_user).lower() == "root"

    if account_id == "(not initialized)":
        user_id = "(not initialized)"
        arn = "(not initialized)"
    elif is_root:
        # Real AWS: root ARN is `arn:aws:iam::<account-id>:root` — NO `user/` prefix.
        user_id = account_id
        arn = f"arn:aws:iam::{account_id}:root"
    else:
        user_id = f"AIDA{account_id}:{current_user}"
        arn = f"arn:aws:iam::{account_id}:user/{current_user}"

    region_code = s.get("region", "us-east-1")
    region_human = s.get("region_name", region_code)

    return f"""
<section class="aws-section">
  <div class="s3-page-header">
    <h1>Get caller identity</h1>
  </div>
  <p class="aws-muted">
    Equivalent to <code>aws sts get-caller-identity</code>.
    Confirms the account, user and ARN your current session resolves to.
  </p>

  <h2 class="ec2-section-title">Caller identity</h2>
  <table class="aws-table">
    <tbody>
      <tr>
        <th style="width:30%;">Account</th>
        <td><code>{_esc(account_id)}</code></td>
      </tr>
      <tr>
        <th>UserId</th>
        <td><code>{_esc(user_id)}</code></td>
      </tr>
      <tr>
        <th>Arn</th>
        <td><code>{_esc(arn)}</code></td>
      </tr>
      <tr>
        <th>Region</th>
        <td>{_esc(region_human)} <code class="aws-muted">({_esc(region_code)})</code></td>
      </tr>
    </tbody>
  </table>

  <h2 class="ec2-section-title">Session state</h2>
  <table class="aws-table">
    <tbody>
      <tr>
        <th style="width:30%;">Current user</th>
        <td>
          {f'<a href="/iam/users/{_esc(current_user)}"><code>{_esc(current_user)}</code></a>' if current_user else '<span class="aws-muted">root (not logged in as any IAM user)</span>'}
        </td>
      </tr>
      <tr>
        <th>Auth method</th>
        <td>{'IAM user credentials' if current_user else 'Root account credentials'}</td>
      </tr>
      <tr>
        <th>Account tags</th>
        <td>
          {' '.join(f'<span class="aws-tag">{_esc(k)}={_esc(v)}</span>' for k, v in (s.get("tags") or {}).items()) or '<span class="aws-muted">none</span>'}
        </td>
      </tr>
    </tbody>
  </table>

  <h2 class="ec2-section-title">Assumed roles</h2>
  <div class="aws-notice aws-notice-info">
    <strong>AssumeRole / AssumeRoleWithSAML / AssumeRoleWithWebIdentity</strong>
    are not simulated in MiniAWS. Real STS returns temporary credentials
    (<code>AccessKeyId</code>, <code>SecretAccessKey</code>, <code>SessionToken</code>,
    <code>Expiration</code>) for a role. MiniAWS has no roles, so this is informational.
  </div>

  <h2 class="ec2-section-title">CLI equivalent</h2>
  <pre class="iam-json" style="background:#fafafa; color:#16191f; padding:12px;">aws sts get-caller-identity</pre>
  <p class="aws-muted s3-footer-hint">
    Run that command in Termux — the JSON output should match the table above.
  </p>
</section>"""
