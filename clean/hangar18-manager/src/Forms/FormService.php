<?php

declare(strict_types=1);

namespace VisualDesignerManager\Forms;

use VisualDesignerManager\Model\LayoutModel;

final class FormService
{
    private const ACTION = 'h18_vd_submit_form';
    private const NONCE_ACTION = 'h18_vd_front_form';

    public static function register(): void
    {
        add_action('admin_post_' . self::ACTION, [self::class, 'submit']);
        add_action('admin_post_nopriv_' . self::ACTION, [self::class, 'submit']);
    }

    /** @param array<string,mixed> $props */
    public static function renderNode(string $kind, string $nodeId, array $props, string $baseStyle): string
    {
        if (!in_array($kind, ['contactform', 'membershipform'], true)) {
            return '';
        }

        $membership = $kind === 'membershipform';
        $heading = trim((string) ($props['heading'] ?? ($membership ? 'Bliv medlem' : 'Kontakt os')));
        $intro = trim((string) ($props['intro'] ?? ''));
        $buttonText = trim((string) ($props['buttonText'] ?? ($membership ? 'Send indmeldelse' : 'Send besked')));
        $background = sanitize_hex_color((string) ($props['background'] ?? '#f4f1e8')) ?: '#f4f1e8';
        $fieldBackground = sanitize_hex_color((string) ($props['fieldBackground'] ?? '#ffffff')) ?: '#ffffff';
        $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#30382a')) ?: '#30382a';
        $accent = sanitize_hex_color((string) ($props['accentColor'] ?? '#30382a')) ?: '#30382a';
        $padding = max(0, min(80, (int) ($props['padding'] ?? 24)));
        $fieldGap = max(0, min(80, (int) ($props['fieldGap'] ?? 16)));
        $textareaHeight = max(80, min(400, (int) ($props['textareaHeight'] ?? 168)));
        $consentMargin = max(0, min(80, (int) ($props['consentMargin'] ?? 18)));
        $buttonPaddingX = max(0, min(80, (int) ($props['buttonPaddingX'] ?? 20)));
        $buttonPaddingY = max(0, min(60, (int) ($props['buttonPaddingY'] ?? 11)));
        $showPhone = !array_key_exists('showPhone', $props) || !empty($props['showPhone']);
        $requireConsent = !array_key_exists('requireConsent', $props) || !empty($props['requireConsent']);
        $postId = get_the_ID();
        $formId = 'h18-form-' . sanitize_html_class($nodeId);
        $style = $baseStyle
            . 'background:' . $background . ';color:' . $textColor . ';padding:' . $padding . 'px;'
            . '--h18-form-field-bg:' . $fieldBackground . ';--h18-form-accent:' . $accent . ';'
            . '--vdm-form-field-gap:' . $fieldGap . 'px;--vdm-form-textarea-height:' . $textareaHeight . 'px;'
            . '--vdm-form-consent-margin:' . $consentMargin . 'px;--vdm-form-button-padding-x:' . $buttonPaddingX . 'px;'
            . '--vdm-form-button-padding-y:' . $buttonPaddingY . 'px;';

        $html = self::style() . '<section id="h18-clean-' . esc_attr($nodeId) . '" class="h18-clean-front-node h18-vd-form h18-vd-form--' . esc_attr($kind) . '" style="' . esc_attr($style) . '">';
        if ($heading !== '') {
            $html .= '<h2>' . esc_html($heading) . '</h2>';
        }
        if ($intro !== '') {
            $html .= '<p class="h18-vd-form-intro">' . esc_html($intro) . '</p>';
        }
        $html .= self::statusMessage($kind, $nodeId);
        $html .= '<form id="' . esc_attr($formId) . '" class="h18-vd-form-body" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        $html .= '<input type="hidden" name="action" value="' . esc_attr(self::ACTION) . '">';
        $html .= '<input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '">';
        $html .= '<input type="hidden" name="node_id" value="' . esc_attr($nodeId) . '">';
        $html .= '<input type="hidden" name="form_kind" value="' . esc_attr($kind) . '">';
        $html .= '<input type="hidden" name="_h18_vd_form_nonce" value="' . esc_attr(wp_create_nonce(self::NONCE_ACTION)) . '">';
        $html .= '<label class="h18-vd-form-hp" aria-hidden="true">Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label>';
        $html .= '<div class="h18-vd-form-grid">';
        $html .= self::input('name', 'Navn', 'text', true, 'name');
        $html .= self::input('email', 'E-mail', 'email', true, 'email');
        if ($showPhone || $membership) {
            $html .= self::input('phone', 'Telefon', 'tel', $membership, 'tel');
        }
        if ($membership) {
            $html .= self::input('address', 'Adresse', 'text', true, 'street-address');
            $html .= self::input('postal', 'Postnr.', 'text', true, 'postal-code');
            $html .= self::input('city', 'By', 'text', true, 'address-level2');
            $html .= self::textarea('message', 'Kommentar', false);
        } else {
            $html .= self::input('subject', 'Emne', 'text', true, 'off');
            $html .= self::textarea('message', 'Besked', true);
        }
        $html .= '</div>';
        if ($requireConsent) {
            $html .= '<label class="h18-vd-form-consent"><input type="checkbox" name="fields[consent]" value="1" required> <span>Jeg accepterer, at oplysningerne bruges til at besvare min henvendelse.</span></label>';
        }
        $html .= '<button class="h18-vd-form-submit" type="submit">' . esc_html($buttonText !== '' ? $buttonText : 'Send') . '</button>';
        $html .= '</form></section>';
        return $html;
    }

    public static function submit(): void
    {
        $postId = isset($_POST['post_id']) ? absint($_POST['post_id']) : 0;
        $nodeId = sanitize_key((string) wp_unslash($_POST['node_id'] ?? ''));
        $kind = sanitize_key((string) wp_unslash($_POST['form_kind'] ?? ''));
        $nonce = sanitize_text_field((string) wp_unslash($_POST['_h18_vd_form_nonce'] ?? ''));

        if ($postId <= 0 || get_post_type($postId) !== 'page' || !wp_verify_nonce($nonce, self::NONCE_ACTION)) {
            self::redirect($postId, $kind, $nodeId, 'invalid');
        }
        if (!in_array($kind, ['contactform', 'membershipform'], true)) {
            self::redirect($postId, $kind, $nodeId, 'invalid');
        }

        $node = self::nodeConfig($postId, $nodeId, $kind);
        if ($node === null) {
            self::redirect($postId, $kind, $nodeId, 'invalid');
        }

        if (trim((string) wp_unslash($_POST['website'] ?? '')) !== '') {
            self::redirect($postId, $kind, $nodeId, 'sent');
        }

        $raw = isset($_POST['fields']) && is_array($_POST['fields']) ? wp_unslash($_POST['fields']) : [];
        $fields = [];
        foreach ($raw as $key => $value) {
            if (!is_scalar($value)) {
                continue;
            }
            $fields[sanitize_key((string) $key)] = sanitize_textarea_field((string) $value);
        }

        $name = trim((string) ($fields['name'] ?? ''));
        $email = sanitize_email((string) ($fields['email'] ?? ''));
        $phone = trim((string) ($fields['phone'] ?? ''));
        $message = trim((string) ($fields['message'] ?? ''));
        $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
        $requireConsent = !array_key_exists('requireConsent', $props) || !empty($props['requireConsent']);

        $invalid = $name === '' || $email === '' || !is_email($email);
        if ($kind === 'contactform') {
            $invalid = $invalid || trim((string) ($fields['subject'] ?? '')) === '' || $message === '';
        } else {
            $invalid = $invalid
                || $phone === ''
                || trim((string) ($fields['address'] ?? '')) === ''
                || trim((string) ($fields['postal'] ?? '')) === ''
                || trim((string) ($fields['city'] ?? '')) === '';
        }
        if ($requireConsent && empty($fields['consent'])) {
            $invalid = true;
        }
        if ($invalid) {
            self::redirect($postId, $kind, $nodeId, 'invalid');
        }

        $recipient = sanitize_email((string) ($props['recipient'] ?? ''));
        if ($recipient === '' || !is_email($recipient)) {
            $recipient = sanitize_email((string) get_option('admin_email'));
        }
        $recipient = (string) apply_filters('h18_vd_form_recipient', $recipient, $kind, $postId, $nodeId);
        if (!is_email($recipient)) {
            self::redirect($postId, $kind, $nodeId, 'error');
        }

        $site = wp_specialchars_decode((string) get_bloginfo('name'), ENT_QUOTES);
        if ($kind === 'membershipform') {
            $subject = '[' . $site . '] Ny medlemsforespørgsel fra ' . $name;
            $lines = [
                'Ny medlemsforespørgsel',
                '',
                'Navn: ' . $name,
                'E-mail: ' . $email,
                'Telefon: ' . $phone,
                'Adresse: ' . trim((string) ($fields['address'] ?? '')),
                'Postnr.: ' . trim((string) ($fields['postal'] ?? '')),
                'By: ' . trim((string) ($fields['city'] ?? '')),
                'Kommentar: ' . ($message !== '' ? $message : '—'),
            ];
        } else {
            $formSubject = trim((string) ($fields['subject'] ?? 'Kontakt'));
            $subject = '[' . $site . '] Kontakt: ' . $formSubject;
            $lines = [
                'Ny henvendelse fra kontaktformularen',
                '',
                'Navn: ' . $name,
                'E-mail: ' . $email,
                'Telefon: ' . ($phone !== '' ? $phone : '—'),
                'Emne: ' . $formSubject,
                '',
                $message,
            ];
        }
        $lines[] = '';
        $lines[] = 'Side: ' . (string) get_permalink($postId);
        $headers = [
            'Content-Type: text/plain; charset=UTF-8',
            'Reply-To: ' . self::headerName($name) . ' <' . $email . '>',
        ];

        $sent = wp_mail($recipient, $subject, implode("\n", $lines), $headers);
        if (!$sent) {
            self::redirect($postId, $kind, $nodeId, 'error');
        }

        $receiptSubject = $kind === 'membershipform' ? 'Vi har modtaget din medlemsforespørgsel' : 'Vi har modtaget din besked';
        $receiptBody = "Hej " . $name . "\n\nTak for din henvendelse. Vi har modtaget den og vender tilbage hurtigst muligt.\n\n" . $site;
        wp_mail($email, $receiptSubject, $receiptBody, ['Content-Type: text/plain; charset=UTF-8']);

        self::redirect($postId, $kind, $nodeId, 'sent');
    }

    /** @return array<string,mixed>|null */
    private static function nodeConfig(int $postId, string $nodeId, string $kind): ?array
    {
        $model = LayoutModel::get($postId);
        foreach ($model['nodes'] ?? [] as $node) {
            if (!is_array($node)) {
                continue;
            }
            if ((string) ($node['id'] ?? '') === $nodeId && (string) ($node['type'] ?? '') === $kind) {
                return $node;
            }
        }
        return null;
    }

    private static function input(string $name, string $label, string $type, bool $required, string $autocomplete): string
    {
        return '<label class="h18-vd-form-field"><span>' . esc_html($label) . ($required ? ' *' : '') . '</span><input type="' . esc_attr($type) . '" name="fields[' . esc_attr($name) . ']"' . ($required ? ' required' : '') . ' autocomplete="' . esc_attr($autocomplete) . '"></label>';
    }

    private static function textarea(string $name, string $label, bool $required): string
    {
        return '<label class="h18-vd-form-field is-wide"><span>' . esc_html($label) . ($required ? ' *' : '') . '</span><textarea name="fields[' . esc_attr($name) . ']" rows="5"' . ($required ? ' required' : '') . '></textarea></label>';
    }

    private static function statusMessage(string $kind, string $nodeId): string
    {
        $status = sanitize_key((string) wp_unslash($_GET['h18_form_status'] ?? ''));
        $statusKind = sanitize_key((string) wp_unslash($_GET['h18_form_kind'] ?? ''));
        $statusNode = sanitize_key((string) wp_unslash($_GET['h18_form_node'] ?? ''));
        if ($status === '' || $statusKind !== $kind || $statusNode !== $nodeId) {
            return '';
        }
        if ($status === 'sent') {
            $message = $kind === 'membershipform' ? 'Tak. Din medlemsforespørgsel er sendt.' : 'Tak. Din besked er sendt.';
            return '<p class="h18-vd-form-message is-success">' . esc_html($message) . '</p>';
        }
        if ($status === 'invalid') {
            return '<p class="h18-vd-form-message is-error">Kontrollér de obligatoriske felter og prøv igen.</p>';
        }
        return '<p class="h18-vd-form-message is-error">Formularen kunne ikke sendes. Prøv igen senere.</p>';
    }

    private static function headerName(string $name): string
    {
        $name = preg_replace('/[\r\n]+/', ' ', $name) ?? '';
        return trim($name) !== '' ? trim($name) : 'Website';
    }

    private static function redirect(int $postId, string $kind, string $nodeId, string $status): void
    {
        $base = $postId > 0 ? get_permalink($postId) : home_url('/');
        if (!is_string($base) || $base === '') {
            $base = home_url('/');
        }
        $url = add_query_arg([
            'h18_form_status' => sanitize_key($status),
            'h18_form_kind' => sanitize_key($kind),
            'h18_form_node' => sanitize_key($nodeId),
        ], $base);
        wp_safe_redirect($url . '#h18-form-' . rawurlencode($nodeId));
        exit;
    }

    private static function style(): string
    {
        static $done = false;
        if ($done) { return ''; }
        $done = true;
        return '<style id="h18-vd-form-style-v0175">'
            . '.h18-vd-form{box-sizing:border-box;width:100%;border-radius:6px;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:16px;line-height:1.35;text-align:left}.h18-vd-form h2{margin:0 0 8px;padding:0;color:inherit;font:700 32px/1.2 system-ui,-apple-system,"Segoe UI",sans-serif}.h18-vd-form-intro{margin:0 0 20px;padding:0;color:inherit;font:400 16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}'
            . '.h18-vd-form-body{display:block}.h18-vd-form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--vdm-form-field-gap,16px)}'
            . '.h18-vd-form-field{display:flex;flex-direction:column;gap:6px;min-width:0;font-size:14px;font-weight:600;line-height:1.35;color:inherit}.h18-vd-form-field.is-wide{grid-column:1/-1}'
            . '.h18-vd-form input,.h18-vd-form textarea{box-sizing:border-box;width:100%;min-height:42px;border:1px solid #b8b8b2;border-radius:4px;background:var(--h18-form-field-bg);color:inherit;padding:11px 12px;font:400 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif}.h18-vd-form textarea{height:var(--vdm-form-textarea-height,168px);min-height:var(--vdm-form-textarea-height,168px);resize:vertical}'
            . '.h18-vd-form input:focus,.h18-vd-form textarea:focus{outline:2px solid var(--h18-form-accent);outline-offset:1px}'
            . '.h18-vd-form-consent{display:flex;gap:9px;align-items:flex-start;margin:var(--vdm-form-consent-margin,18px) 0;font-size:14px;font-weight:400;line-height:1.4;color:inherit}.h18-vd-form-consent input{width:auto;min-height:0;margin-top:3px}'
            . '.h18-vd-form-submit{display:inline-block;border:0;border-radius:4px;background:var(--h18-form-accent);color:#fff;padding:var(--vdm-form-button-padding-y,11px) var(--vdm-form-button-padding-x,20px);font:700 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif;cursor:pointer}'
            . '.h18-vd-form-submit:hover{filter:brightness(1.12)}.h18-vd-form-message{padding:10px 12px;border-radius:4px;font-weight:600}.h18-vd-form-message.is-success{background:#e9f5e7}.h18-vd-form-message.is-error{background:#f9e4e2}'
            . '.h18-vd-form-hp{position:absolute!important;left:-10000px!important;width:1px!important;height:1px!important;overflow:hidden!important}'
            . '@media(max-width:782px){.h18-vd-form-grid{grid-template-columns:1fr}.h18-vd-form-field.is-wide{grid-column:auto}}'
            . '</style>';
    }

    private function __construct()
    {
    }
}
