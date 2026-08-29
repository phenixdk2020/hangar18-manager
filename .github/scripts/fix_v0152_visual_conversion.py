from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / 'clean' / 'hangar18-manager' / 'src' / 'Migration' / 'VisualBlockConversionService.php'
text = path.read_text(encoding='utf-8')

text = text.replace(
    "self::containerNode(\n                $containerId, ($i + 1) * 10,\n                self::geometry",
    "self::containerNode(\n                $containerId, $parentId, ($i + 1) * 10,\n                self::geometry",
    1,
)
text = text.replace(
    "self::containerNode(\n            $containerId, $order,\n            self::geometry",
    "self::containerNode(\n            $containerId, $parentId, $order,\n            self::geometry",
    1,
)
text = text.replace(
    "private static function containerNode(string $id, int $order, array $geometry, string $background, int $radius, int $padding): array",
    "private static function containerNode(string $id, string $parentId, int $order, array $geometry, string $background, int $radius, int $padding): array",
    1,
)
text = text.replace(
    "'id' => $id, 'type' => 'container', 'parentId' => '', 'order' => $order,",
    "'id' => $id, 'type' => 'container', 'parentId' => $parentId, 'order' => $order,",
    1,
)
text = text.replace("mb_strlen($label)", "self::textLength($label)")
text = text.replace("mb_strlen($text)", "self::textLength($text)")
needle = "    private function __construct()\n    {\n    }\n"
helper = "    private static function textLength(string $value): int\n    {\n        return function_exists('mb_strlen') ? (int) mb_strlen($value) : strlen($value);\n    }\n\n" + needle
if needle not in text:
    raise SystemExit('constructor marker missing')
text = text.replace(needle, helper, 1)

path.write_text(text, encoding='utf-8')
print('Applied v0.1.52 parent hierarchy and mbstring safety fixes')
