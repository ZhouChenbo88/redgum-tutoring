# Redgum Centre Desk — Zhang edition

An independent Node.js implementation of the Redgum Tutoring case. A local web application with vanilla HTML/CSS/JavaScript and no external runtime libraries. Fictional classroom records only: this demo has no authentication, authorization, payments, room or overlapping-booking detection.

## Run from a clean checkout

Prerequisite: Node.js 22 or later (Node 24 is the development runtime). No `npm install` or database service is required.

Published source: [Zhang's zhangyanming branch](https://github.com/ZhouShenbo88/redgum-tutoring/tree/zhangyanming). To obtain this independent Node implementation:

```sh
git clone --branch zhangyanming https://github.com/ZhouShenbo88/redgum-tutoring.git redgum-zhang
cd redgum-zhang
```

```sh
node server.js
```

Open `http://127.0.0.1:3000`. The first run is deliberately empty. Add a fictional student (name, year 5–12, family contact, subjects), a fictional tutor (name and subjects), and a tutor availability window on the chosen weekday. Book a 60- or 90-minute session matching that tutor's subject. A booking must start and end inside one single window. New sessions always start booked (any supplied creation status is ignored); editing allows attended, cancelled, or missed. Centre day/week, student history, and that tutor's future booked sessions are available in the Schedule area.

Student/tutor edits and deactivation are in their work areas. Use “Edit / move” for sessions, “Cancel” to retain a cancelled record, and Edit/Remove for availability. Inactive tutors are excluded from new-booking lists; inactive students are also excluded under the documented assumption below. Historic sessions remain viewable.

The new-session form displays a disabled booked status. When editing a saved session, the status selector becomes available; clearing or saving the form returns it to booked-only creation mode.

For optional configuration, copy `.env.example` to `.env`, use illustrative local values, then run:

```sh
npm start
```

`npm start` reads `.env` if present; `node server.js` reads process environment values only. The configuration variables are `HOST`, `PORT`, `DATA_FILE`, and `TZ`. Defaults are loopback, port 3000, `data/schedule.json`, and `Australia/Brisbane`. Match `TZ` to the centre before creating records. Relative `DATA_FILE` paths are relative to the command's working directory; start commands from the repository root. Ensure the data directory is writable. Do not commit `.env` or persisted records.

## Test

```sh
npm test
# equivalently
node --test
```

Tests use temporary fictional data and clean up afterward. They cover window boundaries, weekday matching, single-window containment, invalid-move rollback, inactive records, retained histories, availability-change protection, views, atomic-save failure, restart persistence, and HTTP error responses. Overlap detection is explicitly not implemented. The published [GitHub Actions run 37217130857](https://github.com/ZhouShenbo88/redgum-tutoring/actions/runs/37217130857) was verified successful for its Node 22/24 matrix.

Verified local execution on 2026-09-28: Node v24.19.0, `node --test`, 24 tests passed with no failures. A fresh local Git clone of the source-equivalent pre-rewrite Zhang branch passed all 24 tests; the current rewritten branch was separately verified by the linked GitHub Actions run. The final staged browser check saved fictional student/tutor records, refused an invalid 18:30 one-hour booking outside availability, and displayed a valid 16:00 session as booked. The local clone check is distinct from the successful remote CI run; Docker execution remains unverified.

## Architecture and persistence

`src/scheduler.js` owns validation and transactional state; `server.js` provides HTTP and API routes; `public/` provides the browser interface; `test/` holds meaningful behaviour tests. Mutations clone state, validate, write a unique temporary JSON file beside the final file, flush it, then atomically rename it. Memory is replaced only after a successful save. Failed validation/write leaves the committed in-memory state unchanged. Use one server process per data file; there is no multi-process locking or database-grade recovery. Back up the JSON file while the process is stopped. A corrupt/unsupported file fails startup rather than silently resetting data.

API POST/PATCH requires JSON content type. Write requests carrying an Origin header from a different host are refused; static and API responses use no-store. These checks reduce unintended browser writes to a local demo and do not constitute authentication or access control.

## Domain decisions and scope

- Weekday numbering is 0 Monday through 6 Sunday. Times use HH:MM and stored dates YYYY-MM-DD. New and moved sessions use identical containment checks. A session cannot bridge two adjacent windows.
- Availability editing/removal is refused if it invalidates a future booked session, evaluated in the centre's server timezone. Move/cancel the affected booking first. Historical sessions and future non-booked sessions do not block changes. Another remaining covering window permits removal. This is an explicit policy chosen where the case does not prescribe the workflow.
- New/moved sessions require active students and tutors; rejecting inactive students and checking that the tutor teaches the session subject are documented assumptions. Student subjects are required to record what the student is being tutored in, extending the starter story's minimum name/year/contact fields to satisfy the core record description.
- Status-only changes on historic sessions work after timetable edits. Reopening a cancelled/attended/missed session as booked rechecks current availability and active people.
- Removing a student/tutor means deactivation. Removing a session means cancellation. Only availability windows are physically removed.
- Subjects are entered as comma-separated values. Term-specific effective dates and one-off unavailability are deferred. Weekly windows apply to all dates on that weekday; centre opening-hour restrictions are not additionally hard-coded. Browser date defaults use Brisbane time; keep the configured server timezone as Australia/Brisbane to match them.
- Room allocation/clashes, overlap/double-booking detection, invoices, packs, payments, payroll, reminders, self-service, video links, blue-card tracking, accounting reports and special events are outside committed scope.

## Deployment configuration

Docker configuration is supplied for review. Container execution requires Docker and has not been established merely by creating this file:

```sh
docker build -t redgum-zhang .
docker run --rm -p 127.0.0.1:3000:3000 -v redgum-zhang-data:/app/data redgum-zhang
```

The persistent volume retains the JSON file across container replacement. The image runs as the built-in `node` user. Node base image and GitHub action tags can change: pin reviewed digests/commit SHAs for a maintained production deployment. This app is a local demo; public deployment requires a separately designed authentication/access model and transport protection.

## Configuration management and publication evidence

Individual GitHub account: **ZhangYanming88**. Its collaborator invitation to the Zhou-owned repository was accepted, and the Zhang implementation was published through the authenticated collaborator account at [ZhouShenbo88/redgum-tutoring, branch zhangyanming](https://github.com/ZhouShenbo88/redgum-tutoring/tree/zhangyanming). The story branch [codex/zhang-rg-core](https://github.com/ZhouShenbo88/redgum-tutoring/tree/codex/zhang-rg-core) was also pushed. The rewritten code/CI baseline is `980e8a9540419a3c9c1204dde39fce29472e4793`. Its Git commit author is **ZhangYanming88** after the authorized history rewrite. The project remains AI-assisted, and commit attribution alone cannot prove independent human authorship. [Remote CI](https://github.com/ZhouShenbo88/redgum-tutoring/actions/runs/37217130857) succeeded on Node 22 and 24. See `docs/PUBLICATION.md` for the evidence boundaries.

The A2 brief describes individual assessment; the case's fixed Definition of Done also requires story branches pushed to the team repository, Jira acceptance-criterion demonstration, another member's PR review with comments addressed, automated tests, clean-checkout setup, no critical defects, and updated Jira/Confluence. Publication, automated checks and local browser evidence are recorded above. Another human member's PR review, Jira demonstrations/status and Confluence decisions/handover remain pending. See `HANDOVER.md`.

Source materials: the user-supplied ISYS3001 A2 Assessment Brief, RFP template and Redgum Tutoring case image. This source repository contains no private student identifiers.
