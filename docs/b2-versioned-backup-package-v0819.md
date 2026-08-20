# B2 — Versioned full-site backup package

**Design baseline:** v0.8.19 backlog slice  
**Public cutover:** not involved  
**Protected domains:** Vehicle / Event / Gallery remain unchanged

## 1. Goal

B2 extends the current loose managed JSON snapshot into a portable, versioned Hangar18 package. A completed package gets one immutable human-readable ID:

`H18-BACKUP-000001`

The ID is never reused, even if a package is later archived or deleted from an external storage location.

## 2. Standard portable package

The normal B2 package is application-aware, not a raw hosting image. It must contain enough data to recreate Hangar18-managed state on another compatible WordPress installation without silently overwriting unrelated content.

Logical payloads:

1. `managed-site`
   - all Hangar18-managed WordPress pages;
   - page ID/source identity, slug, status, parent, excerpt/content and featured media references;
   - current Page Editor state and legacy markers needed for compatibility.
2. `page-versions`
   - managed page version ledger and retained restore metadata.
3. `site-builder`
   - Header/Footer templates and assignments;
   - menu configuration;
   - global/design settings and reusable components/templates.
4. `forms-polls-data`
   - forms, polls/votes and other Hangar18-managed structured site data.
5. `plugin-metadata`
   - package/runtime metadata, schema versions and relevant Hangar18 option-backed state required to interpret the package.
6. `media`
   - manifest entries for files actually referenced by the backed-up state;
   - original media files;
   - required Hangar18-generated derivatives such as `.h18.webp` / `.h18.avif` when referenced or needed for equivalent output.

## 3. Manifest contract

Manifest schema v1.0 contains at minimum:

- `SchemaVersion`;
- immutable `BackupId`;
- `CreatedUtc`;
- `PluginVersion`;
- `SourceSite` with normalized HomeUrl, SiteUrl, Host and source identity SHA-256;
- logical payload entries with canonical UTF-8 JSON byte length, item count and SHA-256;
- media entries with relative path, bytes, MIME type, SHA-256 and derivative entries;
- whole-manifest SHA-256;
- explicit capability flags.

B2-A capability flags are deliberately:

- `FullRestore=false`;
- `SelectiveRestore=false`;
- `ZipExport=false`;
- `DryRunValidation=true`.

A capability may only become true in the slice that implements and tests it.

## 4. Canonical checksums

Associative object keys are recursively sorted before JSON hashing. List order remains significant. This gives deterministic SHA-256 values independent of PHP associative insertion order.

Validation must fail on:

- changed payload content;
- changed manifest content without a matching manifest checksum;
- duplicate logical payload names;
- missing package payloads referenced by the manifest;
- unsafe media paths or case-insensitive duplicate media paths;
- unsupported schema or malformed backup ID.

## 5. Media policy

Package paths are relative package paths only. Absolute paths and `..` traversal are invalid.

On import, media must never silently replace an existing WordPress file. Future B2 restore preflight must classify each item as at least:

- exact checksum match / reusable;
- path collision with different checksum;
- missing target file;
- requires ID remap;
- derivative can be regenerated;
- derivative must be restored from package.

Actual file copying belongs to a later B2 slice and requires an explicit signed/confirmed plan.

## 6. Restore policy

### Full restore

Future full restore must:

1. validate manifest/schema/checksums;
2. compare source and target site identity/runtime compatibility;
3. calculate page/media/URL collisions;
4. create a fresh safety backup before the first mutation;
5. present a dry-run plan;
6. require explicit confirmation bound to the exact package and plan;
7. apply mutations transactionally where practical;
8. retain audit and rollback metadata.

### Selective restore

A page-level restore may reuse B1 semantics where possible:

- replace original only after safety backup;
- or create a collision-safe draft copy;
- unrelated pages, menu assignment and public URLs remain unchanged.

## 7. ZIP export

ZIP belongs to B2-B/B2-C, not B2-A. A package ZIP should eventually use a predictable structure similar to:

```text
H18-BACKUP-000123/
  manifest.json
  payloads/
    managed-site.json
    page-versions.json
    site-builder.json
    forms-polls-data.json
    plugin-metadata.json
  media/
    ... referenced originals and required derivatives ...
```

The manifest remains the authority; ZIP directory listing alone is not trusted.

## 8. Raw database / plugin / theme disaster recovery

### Decision

**Do not include a raw database dump, plugin tree or theme tree in the normal portable B2 package.**

Reasons:

- raw WordPress DB contains unrelated plugins, users, sessions/tokens, mail/integration configuration and potentially secrets/private data;
- serialized PHP data and absolute paths/domains make blind cross-host restore unsafe;
- plugin/theme binaries may be incompatible with the destination PHP/WordPress/hosting stack;
- a DB-level restore can overwrite data outside Hangar18 Manager's ownership boundary;
- normal B2 selective restore would become impossible to reason about safely.

### Separate future `B2-DR` high-risk mode

A true whole-WordPress disaster-recovery package may be investigated as a **separate opt-in mode** only. It must not share the normal one-click restore path.

Minimum gates for B2-DR:

- explicit administrator acknowledgement that the operation can replace the whole WordPress installation;
- hosting/PHP/MySQL/MariaDB/WordPress compatibility report;
- database size and available disk-space checks;
- secret/privacy classification and encrypted-at-rest package requirements;
- target-site maintenance mode;
- fresh host-level/database backup before mutation;
- domain/path rewrite plan with serialized-data-safe tooling;
- plugin/theme version inventory and compatibility checks;
- separate confirmation phrase/token;
- audit and documented host-level rollback procedure.

Until those gates exist, B2-DR remains non-executable.

## 9. Delivery slices

- **B2-A — manifest + deterministic checksum + dry-run schema validation:** implemented as pure/read-only core.
- **B2-B — authoritative snapshot collector + referenced-media inventory:** next; must reuse existing managed-page discovery rather than duplicate it.
- **B2-C — immutable package catalog + ZIP writer/download:** writes package artifacts, no restore yet.
- **B2-D — import/restore dry-run and collision/remap planner:** still non-mutating.
- **B2-E — confirmed selective/full restore with safety backup and audit:** mutation slice.
- **B2-DR — optional whole-WordPress disaster recovery research/implementation:** separate high-risk track.

## 10. Non-negotiable isolation

B2 work does not activate Ultimate Designer public rendering and does not change Vehicle/Event/Gallery, Header/Footer public cutover, menu public cutover, page URLs or I10 release gates.
