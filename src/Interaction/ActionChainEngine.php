<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

use Hangar18\UltimateDesigner\Contracts\InteractionActionHandler;
use Hangar18\UltimateDesigner\Contracts\Logger;
use RuntimeException;
use Throwable;

/** UD-076/080 ordered action-chain executor with deterministic error handling. */
final class ActionChainEngine
{
    /** @var array<string,InteractionActionHandler> */
    private array $handlers = [];
    private Logger $logger;

    /** @param iterable<InteractionActionHandler> $handlers */
    public function __construct(iterable $handlers, Logger $logger)
    {
        foreach ($handlers as $handler) {
            $type = strtolower(trim($handler->type()));
            if ($type === '' || isset($this->handlers[$type])) {
                throw new RuntimeException('Interaction action handler type is empty or duplicated.');
            }
            $this->handlers[$type] = $handler;
        }
        $this->logger = $logger;
    }

    /**
     * @param list<array<string,mixed>> $actions
     * @param array<string,mixed> $context
     * @return array{success:bool,results:list<array<string,mixed>>,failed_index:?int}
     */
    public function execute(array $actions, array $context): array
    {
        $results = [];
        foreach (array_values($actions) as $index => $action) {
            $type = strtolower(trim((string) ($action['Type'] ?? '')));
            $handler = $this->handlers[$type] ?? null;
            if ($handler === null) {
                $message = "No action handler registered for '{$type}'.";
                $this->logger->log('ERROR', 'INTERACTION_ACTION_UNSUPPORTED', $message);
                return ['success'=>false,'results'=>$results,'failed_index'=>$index];
            }
            try {
                $result = $handler->execute(is_array($action['Config'] ?? null) ? $action['Config'] : [], $context);
            } catch (Throwable $exception) {
                $result = ['success'=>false,'message'=>$exception->getMessage()];
            }
            $result['type'] = $type;
            $result['index'] = $index;
            $results[] = $result;
            $level = !empty($result['success']) ? 'INFO' : 'ERROR';
            $this->logger->log($level, 'INTERACTION_ACTION_' . strtoupper($type), (string) ($result['message'] ?? 'Action completed.'));
            if (empty($result['success']) && strtolower((string) ($action['OnError'] ?? 'stop')) !== 'continue') {
                return ['success'=>false,'results'=>$results,'failed_index'=>$index];
            }
        }
        return ['success'=>true,'results'=>$results,'failed_index'=>null];
    }
}
