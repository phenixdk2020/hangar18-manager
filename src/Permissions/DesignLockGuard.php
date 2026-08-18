<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Permissions;

/** UD-095 guards locked structure/design while allowing explicitly released content properties. */
final class DesignLockGuard
{
    /** @var list<string> */
    private array $designPrefixes = [
        'Background','CustomBackground','CustomTextColor','CustomHeadingColor','Border','Shadow','Opacity',
        'Desktop','Tablet','Mobile','TopSpacing','BottomSpacing','Padding','Margin','Width','Height','Font','H1','H2','H3',
        'SectionBodyFont','SectionHeadingFont','Hover','Focus','Active','Animation','Transition','Radius','Gap','Layout'
    ];

    /**
     * @param array<string,mixed> $beforeSection
     * @param array<string,mixed> $afterSection
     * @param array{Structure?:bool,Design?:bool} $lock
     * @param array<string,true> $released property names only for this section
     * @return list<string>
     */
    public function violations(array $beforeSection, array $afterSection, array $lock, array $released = []): array
    {
        $violations = [];
        $keys = array_unique(array_merge(array_keys($beforeSection), array_keys($afterSection)));
        sort($keys);
        foreach ($keys as $property) {
            if (($beforeSection[$property] ?? null) === ($afterSection[$property] ?? null)) { continue; }
            if (isset($released[$property])) { continue; }
            if (!empty($lock['Structure']) && in_array($property, ['Key','Type','Order','LayoutParentKey'], true)) {
                $violations[] = 'structure:' . $property;
                continue;
            }
            if (!empty($lock['Design']) && $this->isDesignProperty($property)) {
                $violations[] = 'design:' . $property;
            }
        }
        return $violations;
    }

    private function isDesignProperty(string $property): bool
    {
        foreach ($this->designPrefixes as $prefix) {
            if (strncmp($property, $prefix, strlen($prefix)) === 0) { return true; }
        }
        return false;
    }
}
