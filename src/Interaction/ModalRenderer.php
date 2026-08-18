<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

/** UD-078 accessible modal shell; body HTML comes from the shared element renderer. */
final class ModalRenderer
{
    /** @param array<string,mixed> $modal */
    public function render(array $modal, string $bodyHtml): string
    {
        $id = $this->esc((string) ($modal['Id'] ?? 'modal'));
        $title = $this->esc((string) ($modal['Title'] ?? 'Dialog'));
        $labelId = 'h18-modal-title-' . $id;
        return '<div class="h18-modal" data-h18-modal="' . $id . '" hidden>'
            . '<div class="h18-modal-overlay" data-h18-modal-close></div>'
            . '<div class="h18-modal-dialog" role="dialog" aria-modal="true" aria-labelledby="' . $labelId . '" tabindex="-1">'
            . '<div class="h18-modal-header"><h2 id="' . $labelId . '">' . $title . '</h2>'
            . '<button type="button" class="h18-modal-close" data-h18-modal-close aria-label="Luk dialog">×</button></div>'
            . '<div class="h18-modal-body">' . $bodyHtml . '</div>'
            . '</div></div>';
    }

    private function esc(string $value): string
    {
        return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
}
