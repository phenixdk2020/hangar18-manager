<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use RuntimeException;

/** Binds explicit import confirmation to a previously reviewed dry-run plan. */
final class ImportPlanTokenService
{
    private string $secret;
    public function __construct(string $secret){$secret=trim($secret);if(strlen($secret)<32){throw new RuntimeException('Import plan token secret must be at least 32 characters.');}$this->secret=$secret;}

    /** @param array<string,mixed> $plan */
    public function issue(string $packageChecksum,string $strategy,array $plan,int $ttl=900): array
    {
        $expires=time()+max(60,min(3600,$ttl));$planHash=$this->planHash($plan);$payload=$packageChecksum.'|'.$strategy.'|'.$planHash.'|'.$expires;$mac=hash_hmac('sha256',$payload,$this->secret);
        return ['token'=>self::b64($payload.'|'.$mac),'expires'=>$expires,'planHash'=>$planHash];
    }

    /** @param array<string,mixed> $plan */
    public function verify(string $token,string $packageChecksum,string $strategy,array $plan): bool
    {
        $decoded=self::unb64($token);if($decoded===''){return false;}$parts=explode('|',$decoded);if(count($parts)!==5){return false;}
        [$checksum,$storedStrategy,$planHash,$expires,$mac]=$parts;if(!ctype_digit($expires)||(int)$expires<time()){return false;}
        if(!hash_equals($checksum,$packageChecksum)||!hash_equals($storedStrategy,$strategy)||!hash_equals($planHash,$this->planHash($plan))){return false;}
        $payload=$checksum.'|'.$storedStrategy.'|'.$planHash.'|'.$expires;$expected=hash_hmac('sha256',$payload,$this->secret);return hash_equals($expected,$mac);
    }

    /** @param array<string,mixed> $plan */
    private function planHash(array $plan): string
    {
        $stable=['Strategy'=>(string)($plan['Strategy']??''),'Valid'=>(bool)($plan['Valid']??false),'Mappings'=>$plan['Mappings']??[],'Conflicts'=>$plan['Conflicts']??[],'Actions'=>$plan['Actions']??[]];
        return (new CanonicalJson())->hash($stable);
    }
    private static function b64(string $value): string{return rtrim(strtr(base64_encode($value),'+/','-_'),'=');}
    private static function unb64(string $value): string{$value=strtr(trim($value),'-_','+/');$pad=strlen($value)%4;if($pad){$value.=str_repeat('=',4-$pad);}$decoded=base64_decode($value,true);return is_string($decoded)?$decoded:'';}
}
