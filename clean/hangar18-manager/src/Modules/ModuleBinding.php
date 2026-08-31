<?php

declare(strict_types=1);

namespace VisualDesignerManager\Modules;

final class ModuleBinding
{
    public const SCHEMA = 1;

    /** @param mixed $raw @return array<string,mixed> */
    public static function normalize($raw): array
    {
        $raw = is_array($raw) ? $raw : [];
        $mode = strtolower((string) ($raw['mode'] ?? 'static'));
        if (!in_array($mode, ['static', 'module'], true)) {
            $mode = 'static';
        }

        $module = ModuleRegistry::key((string) ($raw['module'] ?? ''));
        if ($mode === 'module' && !ModuleRegistry::supports($module)) {
            $mode = 'static';
            $module = '';
        }
        if ($mode === 'static') {
            $module = '';
        }

        $view = strtolower((string) ($raw['view'] ?? 'list'));
        if (!in_array($view, ['list', 'detail'], true)) {
            $view = 'list';
        }

        $recordId = strtolower(trim((string) ($raw['recordId'] ?? '')));
        if (!preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) {
            $recordId = '';
        }

        $query = isset($raw['query']) && is_array($raw['query']) ? $raw['query'] : [];
        $status = strtolower((string) ($query['status'] ?? 'publish'));
        if (!in_array($status, ['draft', 'publish', 'archive', 'all'], true)) {
            $status = 'publish';
        }
        $orderBy = (string) ($query['orderBy'] ?? 'sortOrder');
        if (!in_array($orderBy, ['sortOrder', 'title', 'updatedAt'], true)) {
            $orderBy = 'sortOrder';
        }
        $order = strtoupper((string) ($query['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';
        $limit = is_numeric($query['limit'] ?? null) ? (int) $query['limit'] : 50;
        $limit = max(1, min(100, $limit));

        $fieldMap = [];
        if (isset($raw['fieldMap']) && is_array($raw['fieldMap'])) {
            foreach ($raw['fieldMap'] as $target => $source) {
                $target = sanitize_key((string) $target);
                $source = sanitize_key((string) $source);
                if ($target !== '' && $source !== '') {
                    $fieldMap[$target] = $source;
                }
                if (count($fieldMap) >= 100) {
                    break;
                }
            }
        }

        return [
            'schema' => self::SCHEMA,
            'mode' => $mode,
            'module' => $module,
            'view' => $view,
            'recordId' => $view === 'detail' ? $recordId : '',
            'query' => [
                'status' => $status,
                'orderBy' => $orderBy,
                'order' => $order,
                'limit' => $limit,
            ],
            'fieldMap' => $fieldMap,
        ];
    }

    public static function isDynamic(array $binding): bool
    {
        return ($binding['mode'] ?? 'static') === 'module'
            && ModuleRegistry::supports((string) ($binding['module'] ?? ''));
    }

    private function __construct()
    {
    }
}
