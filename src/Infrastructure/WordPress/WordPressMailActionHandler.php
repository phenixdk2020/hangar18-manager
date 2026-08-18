<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\InteractionActionHandler;

/** UD-076 WordPress mail action with field-token interpolation and bounded headers. */
final class WordPressMailActionHandler implements InteractionActionHandler
{
    public function type(): string { return 'mail'; }

    public function execute(array $config, array $context): array
    {
        $to = trim((string) ($config['To'] ?? ''));
        if (filter_var($to, FILTER_VALIDATE_EMAIL) === false) {
            return ['success'=>false,'message'=>'Mail recipient is invalid.'];
        }
        $values = is_array($context['values'] ?? null) ? $context['values'] : [];
        $subject = $this->tokens((string) ($config['Subject'] ?? 'Formularbesked'), $values);
        $body = $this->tokens((string) ($config['Body'] ?? ''), $values);
        $headers = ['Content-Type: text/plain; charset=UTF-8'];
        $replyField = trim((string) ($config['ReplyToField'] ?? ''));
        if ($replyField !== '') {
            $replyTo = trim((string) ($values[$replyField] ?? ''));
            if (filter_var($replyTo, FILTER_VALIDATE_EMAIL) !== false) {
                $headers[] = 'Reply-To: ' . $replyTo;
            }
        }
        $ok = wp_mail($to, $subject, $body, $headers);
        return ['success'=>(bool) $ok,'message'=>$ok ? 'Mail sent.' : 'WordPress could not send mail.'];
    }

    /** @param array<string,mixed> $values */
    private function tokens(string $template, array $values): string
    {
        return preg_replace_callback('/\{\{([a-z][a-z0-9_]*)\}\}/i', static function (array $match) use ($values): string {
            $value = $values[$match[1]] ?? '';
            return is_scalar($value) ? (string) $value : '';
        }, $template) ?? $template;
    }
}
