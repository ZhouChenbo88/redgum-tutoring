# ZhouShenbo88 Flask implementation: source handover

This is an AI-assisted source handover, not a published Confluence page. The IDs below are local requirement/story identifiers derived from the supplied Redgum case, not Jira issue keys. The public repository and `main`/`codex/zhou-rg-core` pushes are verified under the authenticated ZhouShenbo88 account. Remote `main` pytest [run 37217105790](https://github.com/ZhouShenbo88/redgum-tutoring/actions/runs/37217105790) completed successfully for account-attributed code baseline `8a1306b91e823bcde15fad976aa25de5fbc888d9`. Jira acceptance demonstrations, genuine human pull-request review and Confluence publication remain pending; no story is certified as satisfying the case's full Definition of Done.

## 1. What was delivered against scope

| Local story ID | Capability implemented | Code/evidence |
| --- | --- | --- |
| ST-01 / ST-02 | Student records, editing and soft deactivation; school year, family contact and subjects; persistent identity | `app.py` student schema/validator and `/api/students`; CRUD and persistence tests |
| TU-01 / TU-02 | Tutor names/subjects and soft deactivation preserving existing sessions; reject new/moved bookings for inactive people | `app.py` tutor routes and session validation; deactivation/history tests |
| AV-01 | Zero or multiple weekday availability windows; add/edit/delete; proposed changes cannot invalidate future booked sessions | Availability CRUD and transaction validation; boundary, weekday, cross-window and rollback tests |
| SE-01 / SE-02 | Create/edit/move/cancel sessions; 60 or 90 minutes; booked/attended/cancelled/missed; cancellation preserves the record | Session CRUD/validation; valid move, failed move without data loss and cancellation tests |
| VI-02 | Tutor-specific upcoming booked-session filter; valid empty result | `/api/tutors/<id>/upcoming` and `/my-schedule`; filter/empty-state test |
| VI-01 / VI-03 | Centre day/week schedules and student past/future history views | Completed browser UI and API schedule/history filters; local regression checks |
| PE-01 | SQLite persistence, environment configuration, local test suite, example deployment configuration | `README.md`, `.env.example`, `Dockerfile`, CI configuration and app-recreation test |

The final staged application was exercised under Waitress in a real browser: student/tutor CRUD, an out-of-window booking refusal and a valid booking succeeded. A fresh local Git clone passed 41 tests. The separately identified GitHub Actions pytest run succeeded. These checks do not establish every human acceptance criterion, a separately reproduced clean GitHub download or a tested public deployment.

## 2. What was not delivered and why

The local backlog is this section plus section 6; no Jira product backlog has been created. Authentication and staff/tutor role permissions are deferred because this is a fictional-data localhost demonstration. Repository publication and the actual story-branch push are complete. PR peer review, Jira updates and Confluence handover publication still require genuine human participation and separate service evidence.

The case excludes room allocation/clashes, overlap/double-booking detection, invoices, prepaid packs, payments, tutor timesheets/payroll, email/SMS, a parent portal/self-service booking, video links, blue-card tracking, accountant reports and the January intensive. These remain deferred rather than being claimed as delivered. Additional interview/paper wishes—term validity and dated availability exceptions, mid-term timetable changes, reminders, tutor gaps/free-hour reports, printable schedules, lesson coverage notes, long-absent-student reports, NAPLAN and pizza-night activities—need explicit prioritization and acceptance criteria. Cancellation charges and make-up credit belong to a future billing decision.

## 3. Setup and run instructions from GitHub

The verified public repository is `https://github.com/ZhouShenbo88/redgum-tutoring`, with default branch `main`; `codex/zhou-rg-core` was also pushed. The account-attributed integration commit is `d1cda9c2389c4f7fc283fd1b307e1b1f99004cd9` and the verified code/CI baseline is `8a1306b91e823bcde15fad976aa25de5fbc888d9`. The previous source-equivalent local clone passed 41 tests before history rewriting; the rewritten code baseline has a separate successful remote CI run. Clone the repository and follow `README.md`: create a Python 3.12 virtual environment, install `requirements-dev.txt`, run the Flask factory on localhost, and run `python -m pytest -q`. A fresh local Git clone passed 41 tests; a separate clean remote download has not been established by that result. The final staged Waitress/browser checks succeeded as described in section 1, and the linked remote pytest workflow completed successfully. SQLite stores records across restart; preserve the database when copying an installation. The Docker configuration uses Waitress and a persistent `/data` volume; the verified CI workflow runs pytest and does not establish a container build or restart/restore check.

## 4. Known issues and limitations

The tutor-specific view is an ID filter, not authenticated identity; the program must use fictional data only. Subject compatibility and inactive-student booking refusal are explicit implementation decisions that require client confirmation. Availability changes protect future booked sessions in the centre's Queensland time (UTC+10); they do not rewrite attended, missed or cancelled history. Times are same-day weekly windows, without dated exceptions or a term calendar. Durations are 60/90 minutes. Overlap detection is outside this scope. The SQLite schema has no automated upgrade migration, and managed backups/restore drills are pending. Development secret settings must not be reused for an external deployment. Recorded local browser and remote pytest checks do not complete human workflow evidence or production deployment verification.

## 5. Credentials configuration and environment

`APP_ENV` selects development/production; `APP_DATABASE` selects the SQLite file; `SECRET_KEY` signs Flask sessions. `.env.example` is illustrative text and is not automatically loaded by Flask; set environment variables explicitly. Production startup rejects the missing/default secret. CSRF tokens are obtained from `/api/csrf` and accompany write requests, but CSRF does not supply authentication. There are no user accounts or test login credentials. Fictional examples use addresses under `example.invalid`. Do not place passwords, access tokens, real family contacts or private student IDs in a public repository.

## 6. Recommended next sprint backlog

| Priority / local backlog ID | Item | Reason |
| --- | --- | --- |
| 1 / NEXT-01 | Obtain the member's review of recorded browser/test results against all acceptance criteria | Local verification does not establish another person's acceptance |
| 2 / NEXT-02 | Obtain genuine PR peer review and verify CI again after material code changes | Repository, story branch and identified pytest run are verified; human review remains outstanding |
| 3 / NEXT-03 | Create actual Jira mappings and publish this handover/decisions in Confluence | Local IDs and Markdown do not satisfy these service requirements |
| 4 / NEXT-04 | Add authenticated roles before handling real records | ID filtering provides no privacy boundary |
| 5 / NEXT-05 | Confirm subject/inactive-student and availability-history policies with the client | Derived assumptions affect legitimate bookings |
| 6 / NEXT-06 | Specify term dates and dated availability exceptions | Weekly windows cannot represent all paper timetable examples |
| 7 / NEXT-07 | Exercise a clean remote download and deployment backup/restore | The verified fresh local clone does not establish remote download or reproducible recovery |
| 8 / NEXT-08 | Evaluate requested reports/printing/reminders as separate stories | Interview wishes need explicit scope and measurable acceptance criteria |
