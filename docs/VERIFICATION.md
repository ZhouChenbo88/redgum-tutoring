# Zhang implementation — verified evidence

## Actual local automated execution

On 2026-09-28, the independent Node implementation was tested from its repository directory using the bundled Node executable:

```text
C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe --test
Node version: v24.19.0
Tests: 24
Passed: 24
Failed: 0
Cancelled: 0
Skipped: 0
Todo: 0
Final test duration observed: 395.6361 ms
```

These are actual local test results, not a GitHub CI result. Temporary fictional data was used and cleaned up by the test fixtures.

Coverage includes: Monday-zero weekday/calendar validation; exact 60/90-minute window boundaries; before/after-window refusal; wrong weekday/no window; refusal to span adjacent windows; invalid-move memory/disk rollback; tutor/time/duration changes; inactive students/tutors with historical preservation; cancellation without deletion; future-booked protection when windows change; an alternative remaining window; history/status updates after timetable changes; tutor-isolated future booked lists and empty lists; centre day/week and student history; allowed statuses/durations; required fields; year 5–12; creation status fixed booked; window and subject validation; restart persistence; atomic-save error rollback/temporary cleanup; intentionally absent overlap detection; real HTTP CRUD/error/header/foreign-origin checks.

`node --check public/app.js` also completed successfully. A later UI clarification disables the creation-status selector, enables it only while editing an existing session, and restores booked-only mode on reset. This reversible interface change was syntax-checked; the backend's fixed creation status already has a passing behavioural test.

## Browser evidence

The root reviewer will append actual browser actions and screenshots after completing them. This document does not claim a browser check merely because the interface source exists.

## External and deployment evidence

GitHub fresh-clone verification, real Git activity, actual remote CI execution, Docker execution, Jira criterion demonstrations, Confluence publication, and another human member's PR review must be recorded with real evidence. They remain unclaimed here until performed. AI review does not substitute for the fixed case requirement for another team member's review.

Use this evidence record with the six-section `HANDOVER.md` and the A2 configuration-management report. Do not treat an unchecked external requirement as completed.
