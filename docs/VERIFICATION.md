# Local verification record

Date: 28 September 2026 (Asia/Shanghai). Runtime: Python 3.12.14; Flask 3.1.3; pytest 9.1.1. Location: the `redgum-baseline` project directory. The project `.venv` was created with the bundled Python runtime and its declared dependencies were installed successfully.

Executed command in PowerShell:

```powershell
& '.\.venv\Scripts\python.exe' -m pytest -q
```

Actual final result:

```text
.........................................                                [100%]
41 passed in 1.35s
```

The 41 collected test cases cover HTTP API CRUD, student years 5–12 and required family contact, student subjects, HTML form persistence/invalid-save refusal, exact availability boundaries, weekday matching, sessions spanning separate windows, moves changing date/tutor/duration, atomic rejected moves, availability-change rollback and alternative covering windows, historical status preservation, soft deactivation, cancellation, tutor-filtered upcoming/empty API data, SQLite persistence across factory recreation, CSRF and production secret rejection. New sessions must start booked. Durations 60/90 are accepted and other values rejected. Overlap/double-booking detection is outside scope and is not claimed as tested.

This is real local automated output. It does not establish a GitHub Actions run, published repository, remote clean checkout, Docker image startup, Jira demonstration, Confluence publication, human peer review, or exhaustive browser usability/accessibility testing. The tutor page test verifies its HTML application shell and API data; JavaScript-rendered empty-state presentation needs a browser check. Tests use temporary databases and fictional records. Earlier runs exposed missing UI templates and old duration assumptions; the final result above follows the scope correction and template availability.

Student schema and validation now require year 5–12 and nonblank family contact. Existing databases created under the earlier schema are not automatically migrated; the packaged project should begin with no database, and production upgrades require an explicit migration/backup plan.

An actual browser exercise created a fictional year-11 student (Avery Fictional, Physics, parent@example.invalid), tutor (Morgan Example, Physics and Mathematics) and Tuesday 15:30–19:00 window. A 29 September 2026 booking at 18:30 for 60 minutes was rejected without saving; a 16:00/60-minute booking was saved. The corresponding genuine screenshots are `evidence/zhou-rejected.png` and `evidence/zhou-booked.png` in the local delivery package, outside this public source repository. These outcomes verify the two exercised scenarios, not exhaustive browser or operational acceptance.

On 5 October 2026, the separately verified [GitHub Actions pytest run 37217105790](https://github.com/ZhouShenbo88/redgum-tutoring/actions/runs/37217105790) passed for the account-attributed code baseline `8a1306b91e823bcde15fad976aa25de5fbc888d9`. The 28 September local output above does not itself establish that later remote result. See `docs/PUBLICATION.md` for repository and branch evidence. A clean GitHub download, Docker execution, Jira/Confluence activity and another member's human PR review remain unverified.
