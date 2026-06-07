# ISSUE-002: Clean mojibake in Phase 7 reference

- Priority: low
- Type: documentation hygiene
- Status: closed

## Problem

`reference/phase7-ml-training.md` contains mojibake such as `锟?` / `�?` in the
algorithm table and one explanatory sentence.

## Risk

Mostly readability, but malformed table cells can distract agents.

## Candidate Fix

Replace malformed cells with ASCII `none` or `-`; keep the file valid UTF-8.
