<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\AI;

use Hangar18\UltimateDesigner\Portability\CanonicalJson;
use RuntimeException;

/** Binds Accept to the exact pending AI proposal returned by the provider. */
final class AiProposalTokenService
{
    private string $secret;
    public function __construct(string $secret){$secret=trim($secret);if(strlen($secret)<32){throw new RuntimeException('AI proposal token secret must be at least 32 characters.');}$this->secret=$secret;}
    /** @param array<string,mixed> $proposal @return array{token:string,expires:int} */
    public function issue(array $proposal,int $ttl=900): array{$expires=time()+max(60,min(3600,$ttl));$hash=$this->hash($proposal);$payload=$hash.'|'.$expires;$mac=hash_hmac('sha256',$payload,$this->secret);return ['token'=>$this->b64($payload.'|'.$mac),'expires'=>$expires];}
    /** @param array<string,mixed> $proposal */
    public function verify(string $token,array $proposal): bool{$decoded=$this->unb64($token);$parts=explode('|',$decoded);if(count($parts)!==3){return false;}[$hash,$expires,$mac]=$parts;if(!ctype_digit($expires)||(int)$expires<time()||!hash_equals($hash,$this->hash($proposal))){return false;}$expected=hash_hmac('sha256',$hash.'|'.$expires,$this->secret);return hash_equals($expected,$mac);}
    /** @param array<string,mixed> $proposal */
    private function hash(array $proposal): string{return (new CanonicalJson())->hash($proposal);}
    private function b64(string $v): string{return rtrim(strtr(base64_encode($v),'+/','-_'),'=');}
    private function unb64(string $v): string{$v=strtr(trim($v),'-_','+/');$pad=strlen($v)%4;if($pad){$v.=str_repeat('=',4-$pad);}$decoded=base64_decode($v,true);return is_string($decoded)?$decoded:'';}
}
