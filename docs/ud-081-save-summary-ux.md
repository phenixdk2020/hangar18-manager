# E8 save UX enhancement — automatic summary + optional comment

## Goal

A user must be able to press **Gem** without being forced to write a change note every time. The system produces a concise deterministic summary of page changes and stores it in version history. A separate user comment remains optional.

## Browser summary

The page editor compares the originally loaded editor state with the current state and summarizes, where detectable:

- page title changes
- elements added/removed
- element order changes
- content changes
- typography changes
- design changes
- layout changes
- mobile/responsive changes
- dynamic binding/query changes

The preview is shown next to the optional comment field and is recalculated before submit.

## Server fallback

The browser summary is not trusted as the only source. If `page_auto_change_summary` is empty, the server compares the previous persisted page state with the submitted state and produces a fallback summary covering title, added/removed/reordered and changed elements.

## Version history compatibility

Every saved version keeps:

- `ChangeNote`: combined backward-compatible text (`Automatisk: ...` plus optional user comment)
- `AutoChangeSummary`: system-generated summary
- `UserChangeNote`: optional user-entered text

Older version-history readers can continue to use `ChangeNote` without migration.

## UX rule

The old client/server validation that required a handwritten note is removed. WhatIf behavior is unchanged. Save, Ctrl/Cmd+S, backups, page snapshots and revision history continue through the same existing save path.
