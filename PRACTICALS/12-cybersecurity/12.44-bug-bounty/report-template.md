# HackerOne Report Template

## Title
[Stored XSS in Guestbook allows Session Hijacking]

## Severity
High (CVSS: 8.8)

## Description
I found a Stored Cross-Site Scripting (XSS) vulnerability in the guestbook feature. Because the input is not sanitized, an attacker can inject a malicious script that executes in the browser of every user who visits the page.

## Steps to Reproduce
1. Go to `https://example.com/guestbook`
2. In the "Message" field, enter the payload: `<script>alert(document.cookie)</script>`
3. Submit the form.
4. Refresh the page. The script executes again for every visitor.

## Impact
An attacker can steal the session cookies of any user who views the guestbook, allowing them to impersonate the user and take over their account.

## Remediation
Encode all user input before rendering it in the HTML using `htmlspecialchars()` (PHP) or equivalent. Additionally, implement a Content Security Policy (CSP) to block inline scripts.

## Supporting Material
[Attach screenshot of the popup]
[Attach screenshot of the source code showing the unescaped input]
