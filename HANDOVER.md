# ZhouShenbo88 Flask implementation: local handover draft

This is a local, AI-assisted handover draft, not a published Confluence page. The IDs below are local requirement/story identifiers derived from the supplied Redgum case. They are not Jira issue keys. GitHub push, Jira acceptance demonstrations, human pull-request review and Confluence publication remain pending; no story is certified as satisfying the case's full Definition of Done.

## 1. What was delivered against scope

| Local story ID | Capability implemented | Code/evidence |
| --- | --- | --- |
| ST-01 / ST-02 | Student records, editing and soft deactivation; school year, family contact and subjects; persistent identity | `app.py` student schema/validator and `/api/students`; CRUD and persistence tests |
| TU-01 / TU-02 | Tutor names/subjects and soft deactivation preserving existing sessions; reject new/moved bookings for inactive people | `app.py` tutor routes and session validation; deactivation/history tests |
| AV-01 | Zero or multiple weekday availability windows; add/edit/delete; proposed changes cannot invalidate future booked sessions | Availability CRUD and transaction validation; boundary, weekday, cross-window and rollback tests |
| SE-01 / SE-02 | Create/edit/move/cancel sessions; 60 or 90 minutes; booked/attended/cancelled/missed; cancellation preserves the record | Session CRUD/validation; valid move, failed move without data loss and cancellation tests |
| VI-02 | Tutor-specific upcoming booked-session filter; valid empty result | `/api/tutors/<id>/upcoming` and `/my-schedule`; filter/empty-state test |
| PE-01 | SQLite persistence, environment configuration, local test suite, example deployment configuration | `README.md`, `.env.example`, `Dockerfile`, CI configuration and app-recreation test |

Centre day/week views (VI-01) and student past/future views (VI-03) require the completed UI and its real run verification before final acceptance. Local HTTP tests verify selected implemented behaviour; they do not establish every acceptance criterion, hosted CI or clean GitHub checkout evidence.

## 2. What was not delivered and why

The local backlog is this section plus section 6; no Jira product backlog has been created. Authentication and staff/tutor role permissions are deferred because this is a fictional-data localhost demonstration. Repository publication, story branches, PR review, Jira updates and Confluence handover publication require real authorized account access and human participation.

The case excludes room allocation/clashes, overlap/double-booking detection, invoices, prepaid packs, payments, tutor timesheets/payroll, email/SMS, a parent portal/self-service booking, video links, blue-card tracking, accountant reports and the January intensive. These remain deferred rather than being claimed as delivered. Additional interview/paper wishes—term validity and dated availability exceptions, mid-term timetable changes, reminders, tutor gaps/free-hour reports, printable schedules, lesson coverage notes, long-absent-student reports, NAPLAN and pizza-night activities—need explicit prioritization and acceptance criteria. Cancellation charges and make-up credit belong to a future billing decision.

## 3. Setup and run instructions from GitHub

The planned repository is `https://github.com/ZhouShenbo88/redgum-tutoring`, with `main` as the planned default branch. It has not been verified as created or populated. After authorized publication, a new user should clone that real repository and follow `README.md`: create a Python 3.12 virtual environment, install `requirements-dev.txt`, run the Flask factory on localhost, and run `python -m pytest -q`. No clean remote checkout has yet been established. SQLite stores records across restart; preserve the database when copying a running installation. The Docker configuration uses Waitress and a persistent `/data` volume but has not by itself established a tested deployment.

## 4. Known issues and limitations

The tutor-specific view is an ID filter, not authenticated identity; the program must use fictional data only. Subject compatibility and inactive-student booking refusal are explicit implementation decisions that require client confirmation. Availability changes protect future booked sessions in the centre's Queensland time (UTC+10); they do not rewrite attended, missed or cancelled history. Times are same-day weekly windows, without dated exceptions or a term calendar. Durations are 60/90 minutes. Overlap detection is outside this scope. The SQLite schema has no automated upgrade migration, and managed backups/restore drills are pending. Development secret settings must not be reused for an external deployment. UI verification and remote/human workflow evidence remain separate completion gates.

## 5. Credentials configuration and environment

`APP_ENV` selects development/production; `APP_DATABASE` selects the SQLite file; `SECRET_KEY` signs Flask sessions. `.env.example` is illustrative text and is not automatically loaded by Flask; set environment variables explicitly. Production startup rejects the missing/default secret. CSRF tokens are obtained from `/api/csrf` and accompany write requests, but CSRF does not supply authentication. There are no user accounts or test login credentials. Fictional examples use addresses under `example.invalid`. Do not place passwords, access tokens, real family contacts or private student IDs in a public repository.

## 6. Recommended next sprint backlog

| Priority / local backlog ID | Item | Reason |
| --- | --- | --- |
| 1 / NEXT-01 | Verify full UI flow against every core acceptance criterion | Working APIs do not prove desk-staff workflows or all views work |
| 2 / NEXT-02 | Publish under the authorized owner and complete real story branches/PR peer review | The fixed DoD requires authentic repository and human review evidence |
| 3 / NEXT-03 | Create actual Jira mappings and publish this handover/decisions in Confluence | Local IDs and Markdown do not satisfy these service requirements |
| 4 / NEXT-04 | Add authenticated roles before handling real records | ID filtering provides no privacy boundary |
| 5 / NEXT-05 | Confirm subject/inactive-student and availability-history policies with the client | Derived assumptions affect legitimate bookings |
| 6 / NEXT-06 | Specify term dates and dated availability exceptions | Weekly windows cannot represent all paper timetable examples |
| 7 / NEXT-07 | Exercise clean checkout and deployment backup/restore | Persistence alone does not establish reproducible recovery |
| 8 / NEXT-08 | Evaluate requested reports/printing/reminders as separate stories | Interview wishes need explicit scope and measurable acceptance criteria |
