# Redgum Zhang edition — handover preparation

Publication and handover record, 2026-09-28. The independent Node implementation is published on [ZhouShenbo88/redgum-tutoring, branch zhangyanming](https://github.com/ZhouShenbo88/redgum-tutoring/tree/zhangyanming), through authenticated collaborator **ZhangYanming88** after invitation acceptance. This Markdown document is not a published Confluence handover. Jira mapping and another human member's PR review remain pending; no sprint commitment or issue URL is invented.

## 1. What was delivered against scope

Implemented web workflows: student and tutor records with deactivation; weekly tutor availability; session create/edit/move/cancel and status updates; centre day/week schedule, student history, and tutor-specific future booked list. Atomic JSON persistence and automated behavioural/API tests support the implementation. Local `node --test` with Node v24.19.0 passed 24 tests, and a fresh local Git clone of the source-equivalent pre-rewrite tree passed the same 24 tests. The current rewritten branch has a separate successful remote CI run. The final staged browser check saved fictional student/tutor records, refused an invalid 18:30 one-hour booking, and displayed a valid 16:00 booked session. [Remote Actions run 37217130857](https://github.com/ZhouShenbo88/redgum-tutoring/actions/runs/37217130857) succeeded on its Node 22/24 matrix. Link these capabilities to actual Jira stories only after issue creation/verification.

## 2. What was not delivered, and why

Excluded by the core case scope: room allocation/clashes; overlap/double-booking detection; invoices, prepaid packs and payments; payroll; SMS/email sending; portal/self-service; video links; blue-card tracking; accountant reporting; January intensive and other special events. Keep these in the actual product backlog when available. Further wishes from the interviews—free-hour reports, printable tutor sheets, lesson notes and absence reporting—remain deferred. Term-validity dates and exceptional unavailability require more clarified domain work. Authentication was not delivered and records must be fictional. Real Jira/Confluence artifacts and another human member's GitHub PR review remain pending. Docker execution has not been verified.

## 3. Setup and run instructions from GitHub

Clone `https://github.com/ZhouShenbo88/redgum-tutoring.git` with `--branch zhangyanming`, enter the cloned directory, and follow README: Node 22+, `node server.js`, browser at loopback port 3000; `node --test` for checks. The main branch contains a separate implementation, so select Zhang's branch explicitly. No external dependencies or manually precreated data file are needed. The local fresh-clone tests and staged browser actions are verified separately from the successful remote CI. Docker is optional configuration and must be executed in an available runtime before claiming container deployment. See `docs/PUBLICATION.md` for publication evidence.

## 4. Known issues and limitations

Single-process JSON storage has no simultaneous-server coordination and no built-in backup restore UI. No authentication means tutor filtering is a view, not an access-control boundary. Browser date defaults use Brisbane; keep the server timezone at its Brisbane default to match. Current weekly windows do not model term changes or dated exceptions. Subject labels are exact case-sensitive text. Public production use requires further work. Assumptions: refuse availability edits that strand future booked sessions; inactive students cannot receive new/moved sessions; student subjects are required to record tutoring needs; tutor subject must match; preserve historical states. Overlap detection is intentionally outside scope. Keep any discovered critical defect visible and unresolved stories out of Done.

## 5. Credentials, configuration and environment

No logins or credentials exist in this fictional demo. `.env.example` contains illustrative loopback/port/data-path/timezone values; README explains them. `.env` and `data/` are ignored. Use writable persistent storage and only one server process. Never put real contacts, private identifiers, tokens, `.env`, or real records in the public repository. Configure Node 22/24 for local/CI work.

## 6. Recommended next-sprint backlog

1. Resolve real Jira/Confluence mappings and obtain human PR review: required evidence to meet fixed case DoD.
2. Verify user-appropriate authentication and tutor access controls: necessary before real personal records or remote access.
3. Clarify dated availability, term validity and exceptions: reduces mismatch with the supplied paper timetable.
4. Execute the optional container and verify its persistent-volume recovery: fresh local clone tests are complete, but Docker execution remains unverified.
5. Add documented backup/restore and multi-user storage requirements: improves resilience if usage grows.
6. Clarify subject naming and matching: prevents inconsistent labels in a larger tutor list.
7. Agree scope for printable tutor sheets and free-hour reports: requested interview conveniences, currently deferred.
8. Revisit notification and billing integration only with an explicit scope change: these remain outside the case's committed core.

The integration branch `zhangyanming` and story branch `codex/zhang-rg-core` are published; the actual remote CI run linked above succeeded. The rewritten commits show author **ZhangYanming88** and verified code/CI baseline `980e8a9540419a3c9c1204dde39fce29472e4793`. This account metadata does not prove independent human authorship of AI-assisted work. Fixed DoD items currently pending: Jira demonstrations/status, another human member's PR review with comments addressed, and Confluence decisions/handover. An AI review does not establish the required team-member review.
