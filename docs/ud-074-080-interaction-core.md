# UD-074–UD-080 Interaction core

This slice implements the generic Interaction architecture without wiring it into existing Hangar18 pages.

- **UD-074** Generic form schema and semantic server-rendered fields with labels, fieldsets, live status/error regions and keyboard-native controls.
- **UD-075** Server-side validation for required, email/date, min/max length, regex pattern, select/radio options and custom error messages. Passive browser validation enhancement mirrors errors into accessible field regions.
- **UD-076** Ordered submit action chain with explicit stop/continue error policy and logging. Generic mail/save/redirect handlers are separated behind action contracts.
- **UD-077** WordPress webhook handler requires HTTPS, HMAC SHA-256 signing, bounded timeout/retry, zero redirects and `wp_safe_remote_post` SSRF protections.
- **UD-078** Modal definitions reuse the shared Page Schema 1.22 `Sections` tree. The modal shell has `role=dialog`, `aria-modal`, labelled title, Escape handling, focus trap and scroll lock through the passive interaction runtime.
- **UD-079** Popup triggers validate click, time, scroll and context triggers with ANY/ALL composition.
- **UD-080** Declarative client actions support navigate, scroll, open-modal and toggle with safe target/URL validation.

## Compatibility

`assets/interaction-runtime.js` and `.css` are passive release assets. They are not enqueued into the current legacy pages. Existing pages, Vehicle/Event/Gallery and current forms remain unchanged until the approved final conversion phase.

## QA

`tests/Architecture/e7-interaction-smoke.php` covers form schema/rendering, server validation, action ordering/error policy, URL safety, modal accessibility, popup trigger validation and client action serialization. PHP syntax, protected-domain contract and JavaScript syntax remain part of Architecture QA on PHP 8.0/8.2/8.3.
