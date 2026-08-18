<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\InteractionActionHandler;

/** UD-077 signed HTTPS webhook with bounded timeout/retry policy and WP safe HTTP validation. */
final class WordPressWebhookActionHandler implements InteractionActionHandler
{
    public function type(): string { return 'webhook'; }

    public function execute(array $config, array $context): array
    {
        $url = trim((string) ($config['Url'] ?? ''));
        $secret = (string) ($config['Secret'] ?? '');
        $timeout = max(1, min(10, (int) ($config['TimeoutSeconds'] ?? 5)));
        $retries = max(0, min(2, (int) ($config['Retries'] ?? 1)));
        if ($url === '' || strtolower((string) parse_url($url, PHP_URL_SCHEME)) !== 'https') {
            return ['success'=>false,'message'=>'Webhook requires an HTTPS URL.'];
        }
        if (strlen($secret) < 16) {
            return ['success'=>false,'message'=>'Webhook secret must be at least 16 characters.'];
        }

        $payload = [
            'event' => (string) ($config['Event'] ?? 'form.submit'),
            'sent_at' => gmdate('c'),
            'values' => is_array($context['values'] ?? null) ? $context['values'] : [],
            'meta' => is_array($context['meta'] ?? null) ? $context['meta'] : [],
        ];
        $json = wp_json_encode($payload);
        if (!is_string($json)) {
            return ['success'=>false,'message'=>'Webhook payload could not be encoded.'];
        }
        $timestamp = (string) time();
        $signature = hash_hmac('sha256', $timestamp . '.' . $json, $secret);

        $attempt = 0;
        $lastCode = 0;
        do {
            $attempt++;
            $response = wp_safe_remote_post($url, [
                'timeout' => $timeout,
                'redirection' => 0,
                'headers' => [
                    'Content-Type' => 'application/json',
                    'X-H18-Timestamp' => $timestamp,
                    'X-H18-Signature' => 'sha256=' . $signature,
                ],
                'body' => $json,
                'data_format' => 'body',
            ]);
            if (!is_wp_error($response)) {
                $lastCode = (int) wp_remote_retrieve_response_code($response);
                if ($lastCode >= 200 && $lastCode < 300) {
                    return ['success'=>true,'message'=>'Webhook delivered.','data'=>['status'=>$lastCode,'attempts'=>$attempt]];
                }
                if ($lastCode < 500) { break; }
            }
            if ($attempt <= $retries) { usleep(150000 * $attempt); }
        } while ($attempt <= $retries);

        return ['success'=>false,'message'=>'Webhook delivery failed.','data'=>['status'=>$lastCode,'attempts'=>$attempt]];
    }
}
