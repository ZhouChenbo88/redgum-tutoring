# Redgum Zhang edition — handover preparation

Local source preparation, 2026-09-28. This Markdown document is not a published Confluence handover. Jira mapping, actual GitHub activity and human peer review must be completed genuinely. No existing sprint commitment or issue URL is invented.

## 1. What was delivered against scope

Implemented local web workflows: student and tutor records with deactivation; weekly tutor availability; session create/edit/move/cancel and status updates; centre day/week schedule, student history, and tutor-specific future booked list. Atomic JSON persistence and automated behavioural/API tests support the implementation. Local `node --test` with Node v24.19.0 on 2026-09-28 passed 24 tests with no failures. The README contains clean-checkout setup. Link these capabilities to actual Jira stories only after authorized issue creation/verification. The local test result is not evidence of real GitHub/Jira/Confluence activity.

## 2. What was not delivered, and why

Excluded by the core case scope: room allocation/clashes; overlap/double-booking detection; invoices, prepaid packs and payments; payroll; SMS/email sending; portal/self-service; video links; blue-card tracking; accountant reporting; January intensive and other special events. Keep these in the actual product backlog when available. Further wishes from the interviews—free-hour reports, printable tutor sheets, lesson notes and absence reporting—remain deferred. Term-validity dates and exceptional unavailability require more clarified domain work. Authentication was not delivered and records must be fictional. No real Jira/Confluence artifacts, GitHub peer PR review or remote CI run are yet claimed.

## 3. Setup and run instructions from GitHub

Repository URL and actual branch are pending authorized GitHub work. Once supplied, clone that repository, check out the genuine Zhang branch, enter the application directory, and follow README: Node 22+, `node server.js`, browser at loopback port 3000; `node --test` for checks. No external dependencies or manually precreated data file are needed. Docker is optional configuration and must be tested in an available runtime before claiming deployment. Capture an actual clean-checkout run and screenshots before marking the fixed case DoD complete.

## 4. Known issues and limitations

Single-process JSON storage has no simultaneous-server coordination and no built-in backup restore UI. No authentication means tutor filtering is a view, not an access-control boundary. Browser date defaults use Brisbane; keep the server timezone at its Brisbane default to match. Current weekly windows do not model term changes or dated exceptions. Subject labels are exact case-sensitive text. Public production use requires further work. Assumptions: refuse availability edits that strand future booked sessions; inactive students cannot receive new/moved sessions; student subjects are required to record tutoring needs; tutor subject must match; preserve historical states. Overlap detection is intentionally outside scope. Keep any discovered critical defect visible and unresolved stories out of Done.

## 5. Credentials, configuration and environment

No logins or credentials exist in this fictional demo. `.env.example` contains illustrative loopback/port/data-path/timezone values; README explains them. `.env` and `data/` are ignored. Use writable persistent storage and only one server process. Never put real contacts, private identifiers, tokens, `.env`, or real records in the public repository. Configure Node 22/24 for local/CI work.

## 6. Recommended next-sprint backlog

1. Resolve real Jira/Confluence mappings and obtain human PR review: required evidence to meet fixed case DoD.
2. Verify user-appropriate authentication and tutor access controls: necessary before real personal records or remote access.
3. Clarify dated availability, term validity and exceptions: reduces mismatch with the supplied paper timetable.
4. Test a genuine fresh clone and optional container: validates documented deployment independently of the development machine.
5. Add documented backup/restore and multi-user storage requirements: improves resilience if usage grows.
6. Clarify subject naming and matching: prevents inconsistent labels in a larger tutor list.
7. Agree scope for printable tutor sheets and free-hour reports: requested interview conveniences, currently deferred.
8. Revisit notification and billing integration only with an explicit scope change: these remain outside the case's committed core.

Fixed DoD external items currently pending: pushed story branches; Jira demonstrations/status; human PR review; Confluence decisions/handover. A configured workflow does not certify a CI run, and an AI reviewer does not establish another team member's required review.
