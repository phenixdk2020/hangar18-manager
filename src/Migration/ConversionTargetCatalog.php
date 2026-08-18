<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use Hangar18\UltimateDesigner\Compatibility\ProtectedDomainContractCatalog;

/** Defines the fixed I10 order without granting any cutover capability. */
final class ConversionTargetCatalog
{
    /** @var list<string> */
    public const CORE_ORDER=['hjem','om-foreningen','kontakt','bliv-medlem'];

    /** @return list<string> */
    public function coreOrder(): array{return self::CORE_ORDER;}

    /** @return array<string,string> slug => domain */
    public function protectedSlugs(): array
    {
        $out=[];foreach(ProtectedDomainContractCatalog::domains() as $domain){$out[ProtectedDomainContractCatalog::slug($domain)]=$domain;}return $out;
    }

    public function isCore(string $slug): bool{return in_array($this->slug($slug),self::CORE_ORDER,true);}
    public function isProtected(string $slug): bool{return array_key_exists($this->slug($slug),$this->protectedSlugs());}
    public function protectedDomain(string $slug): string{return (string)($this->protectedSlugs()[$this->slug($slug)]??'');}

    /** A comparison page must be deliberately non-critical. */
    public function isComparisonCandidate(string $slug): bool
    {
        $slug=$this->slug($slug);if($slug===''||$this->isCore($slug)||$this->isProtected($slug)){return false;}
        foreach(['editor-test','test','gammel','compare','comparison','sammenlign','kladde','draft'] as $needle){if(strpos($slug,$needle)!==false){return true;}}
        return false;
    }

    private function slug(string $slug): string{return strtolower(trim($slug));}
}
