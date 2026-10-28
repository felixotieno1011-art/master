"""S3 wizards — create-bucket (2-step) and upload-object."""
import html

from core.webui import aws_ref


def _esc(s):
    return html.escape(str(s))


def _region_options(current):
    return "".join(
        f'<option value="{_esc(code)}"{" selected" if code == current else ""}>'
        f'{_esc(label)}</option>'
        for code, label in aws_ref.REGIONS
    )


def render_create_bucket(region_code, error=None):
    err_block = (
        f'<div class="aws-notice aws-notice-error">{_esc(error)}</div>'
        if error else ""
    )
    return f"""
<section class="aws-section">
  <div class="wizard-header">
    <h1>Create bucket</h1>
  </div>
  {err_block}

  <div class="wizard-step-tabs">
    <div class="wizard-step active" data-step="1">1. General configuration</div>
    <div class="wizard-step" data-step="2">2. Review</div>
  </div>

  <form id="create-bucket-form" method="POST" action="/s3/create">
    <div class="wizard-panel active" data-step="1">
      <div class="wizard-field">
        <label for="bucket">Bucket name</label>
        <input id="bucket" name="bucket" type="text" required
               placeholder="my-new-bucket"
               pattern="[a-z0-9][a-z0-9.\\-]{{1,61}}[a-z0-9}}"
               title="3-63 chars, lowercase, digits, hyphens, dots">
        <p class="aws-muted wizard-hint">
          Bucket names must be globally unique, 3-63 chars,
          lowercase letters, numbers, hyphens, dots.
        </p>
      </div>

      <div class="wizard-field">
        <label for="region">AWS Region</label>
        <select id="region" name="region_choice" disabled>
          {_region_options(region_code)}
        </select>
        <p class="aws-muted wizard-hint">
          In MiniAWS, the bucket is created in your current region
          (<code>{_esc(region_code)}</code>). To switch, use the top-bar region selector.
        </p>
      </div>

      <div class="wizard-actions">
        <button type="button" class="aws-button-primary" onclick="wizardStep(2)">
          Next
        </button>
        <a class="aws-button-secondary" href="/s3">Cancel</a>
      </div>
    </div>

    <div class="wizard-panel" data-step="2">
      <table class="aws-table" style="margin-bottom:16px;">
        <tbody>
          <tr><th style="width:35%;">Bucket name</th><td><code id="review-name">—</code></td></tr>
          <tr><th>Region</th><td>{_esc(region_code)}</td></tr>
          <tr><th>Object ownership</th><td>ACLs disabled (recommended)</td></tr>
          <tr><th>Block Public Access</th><td>On (default)</td></tr>
        </tbody>
      </table>
      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Create bucket</button>
        <button type="button" class="aws-button-secondary" onclick="wizardStep(1)">Back</button>
      </div>
    </div>
  </form>

  <script>
    function wizardStep(n) {{
      if (n === 2) {{
        const name = document.getElementById('bucket').value;
        if (!name) {{ document.getElementById('bucket').focus(); return; }}
        document.getElementById('review-name').textContent = name;
      }}
      document.querySelectorAll('.wizard-panel').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
      document.querySelectorAll('.wizard-step').forEach(p =>
        p.classList.toggle('active', p.dataset.step == n));
    }}
  </script>
</section>
"""


def render_upload(bucket, error=None):
    err_block = (
        f'<div class="aws-notice aws-notice-error">{_esc(error)}</div>'
        if error else ""
    )
    return f"""
<section class="aws-section">
  <div class="wizard-header">
    <h1>Upload to <code>{_esc(bucket)}</code></h1>
  </div>
  {err_block}

  <div class="wizard-step-tabs">
    <div class="wizard-step active">Upload object</div>
  </div>

  <form method="POST" action="/s3/upload" enctype="multipart/form-data">
    <input type="hidden" name="bucket" value="{_esc(bucket)}">

    <div class="wizard-panel active">
      <div class="wizard-field">
        <label for="file">File (from device)</label>
        <input id="file" name="file" type="file">
        <p class="aws-muted wizard-hint">
          Uploads to the bucket with the original filename as the object key.
        </p>
      </div>

      <div class="wizard-field" style="border-top:1px dashed #d5dbdb; padding-top:16px;">
        <label for="key">Or paste content (fallback for Android file picker)</label>
        <input id="key" name="key" type="text" placeholder="key.txt" style="margin-bottom:8px;">
        <textarea name="body" rows="6" style="width:100%; font-family:monospace;
                  padding:8px; border:1px solid #d5dbdb; border-radius:3px;"
                  placeholder="content to upload"></textarea>
        <p class="aws-muted wizard-hint">
          If a file is chosen above, this textarea is ignored.
        </p>
      </div>

      <div class="wizard-actions">
        <button type="submit" class="aws-button-primary">Upload</button>
        <a class="aws-button-secondary" href="/s3/{_esc(bucket)}">Cancel</a>
      </div>
    </div>
  </form>
</section>
"""
