<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Workflow;

/** UD-084 readable added/removed/moved/property diff for Sections-based states. */
final class StructuredRevisionDiff
{
    /**
     * @param array<string,mixed> $before
     * @param array<string,mixed> $after
     * @return array{added:list<array<string,mixed>>,removed:list<array<string,mixed>>,moved:list<array<string,mixed>>,changed:list<array<string,mixed>>}
     */
    public function diff(array $before, array $after): array
    {
        $a = $this->indexSections($before);
        $b = $this->indexSections($after);
        $added = [];
        $removed = [];
        $moved = [];
        $changed = [];

        foreach ($b as $key => $entry) {
            if (!isset($a[$key])) {
                $added[] = ['Key'=>$key,'Type'=>(string) ($entry['section']['Type'] ?? ''),'Index'=>$entry['index'],'Parent'=>(string) ($entry['section']['LayoutParentKey'] ?? '')];
                continue;
            }
            $old = $a[$key];
            $oldParent = (string) ($old['section']['LayoutParentKey'] ?? '');
            $newParent = (string) ($entry['section']['LayoutParentKey'] ?? '');
            if ($old['index'] !== $entry['index'] || $oldParent !== $newParent) {
                $moved[] = ['Key'=>$key,'FromIndex'=>$old['index'],'ToIndex'=>$entry['index'],'FromParent'=>$oldParent,'ToParent'=>$newParent];
            }
            $props = $this->propertyChanges($old['section'], $entry['section']);
            if ($props !== []) {
                $changed[] = ['Key'=>$key,'Properties'=>$props];
            }
        }
        foreach ($a as $key => $entry) {
            if (!isset($b[$key])) {
                $removed[] = ['Key'=>$key,'Type'=>(string) ($entry['section']['Type'] ?? ''),'Index'=>$entry['index'],'Parent'=>(string) ($entry['section']['LayoutParentKey'] ?? '')];
            }
        }
        return ['added'=>$added,'removed'=>$removed,'moved'=>$moved,'changed'=>$changed];
    }

    /** @param array<string,mixed> $state @return array<string,array{index:int,section:array<string,mixed>}> */
    private function indexSections(array $state): array
    {
        $result = [];
        foreach (array_values(is_array($state['Sections'] ?? null) ? $state['Sections'] : []) as $index => $section) {
            if (!is_array($section)) { continue; }
            $key = trim((string) ($section['Key'] ?? ''));
            if ($key !== '') { $result[$key] = ['index'=>$index,'section'=>$section]; }
        }
        return $result;
    }

    /** @param array<string,mixed> $before @param array<string,mixed> $after @return list<array<string,mixed>> */
    private function propertyChanges(array $before, array $after): array
    {
        $ignore = ['Order','LayoutParentKey'];
        $keys = array_unique(array_merge(array_keys($before), array_keys($after)));
        sort($keys);
        $changes = [];
        foreach ($keys as $key) {
            if (in_array($key, $ignore, true)) { continue; }
            $old = $before[$key] ?? null;
            $new = $after[$key] ?? null;
            if ($old !== $new) {
                $changes[] = ['Property'=>$key,'Before'=>$old,'After'=>$new];
            }
        }
        return $changes;
    }
}
