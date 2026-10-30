"""Elastic IPs page — /ec2/elastic-ips."""
import html

from core import ec2 as ec2_mod


def _esc(s):
    return html.escape(str(s))


def _flash(qs):
    okv = (qs or {}).get("ok") or []
    erv = (qs or {}).get("error") or []
    if okv:
        return f'<div class="aws-notice aws-notice-success">{html.escape(str(okv[0]))}</div>'
    if erv:
        return f'<div class="aws-notice aws-notice-error">{html.escape(str(erv[0]))}</div>'
    return ""


def render_elastic_ips(qs=None):
    flash = _flash(qs)
    eips = ec2_mod.list_addresses()
    unattached = [e for e in eips if not e.get("InstanceId")]

    # Warn if any unattached EIPs (real AWS bills $0.005/hr for each)
    warning = ""
    if unattached:
        monthly = len(unattached) * 0.005 * 24 * 30
        warning = f"""
<div class="aws-notice aws-notice-warn">
  <strong>&#9888; {len(unattached)} unattached Elastic IP(s) detected.</strong>
  Real AWS charges $0.005/hour for each unattached EIP — that's
  <strong>~${monthly:.2f}/month</strong> for these {len(unattached)}.
  Either associate them with a running instance, or release them.
</div>"""

    rows = "".join(f"""
    <tr>
      <td><code>{_esc(e.get('PublicIp'))}</code></td>
      <td><code>{_esc(e.get('AllocationId'))}</code></td>
      <td>
        {f'<a href="/ec2/instances/{_esc(e["InstanceId"])}">{_esc(e["InstanceId"])}</a>'
         if e.get('InstanceId') else '<span class="billing-budget-status billing-over_budget">UNASSOCIATED</span>'}
      </td>
      <td>
        <form method="POST" action="/ec2/eips/release" style="display:inline"
              onsubmit="return confirm('Release {_esc(e.get('PublicIp'))}?')">
          <input type="hidden" name="allocation_id" value="{_esc(e.get('AllocationId'))}">
          <button type="submit" class="aws-link-danger">Release</button>
        </form>
      </td>
    </tr>""" for e in eips) or \
        '<tr><td colspan="4" class="aws-muted" style="text-align:center; padding:24px;">No Elastic IPs.</td></tr>'

    return f"""
<section class="aws-section">
  {flash}
  {warning}
  <div class="s3-page-header">
    <h1>Elastic IPs <span class="aws-muted">({len(eips)})</span></h1>
    <form method="POST" action="/ec2/eips/allocate" style="display:inline">
      <button type="submit" class="aws-button-primary">Allocate Elastic IP</button>
    </form>
  </div>
  <table class="aws-table">
    <thead>
      <tr><th>Public IP</th><th>Allocation ID</th><th>Instance</th><th>Actions</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="aws-muted s3-footer-hint">
    Real AWS charges for unattached Elastic IPs to discourage hoarding.
    <strong>Always release EIPs you're not using.</strong>
  </p>
</section>"""
