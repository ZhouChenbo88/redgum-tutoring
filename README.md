# Redgum Tutoring — ZhouChenbo88 Flask version

A standalone Flask and SQLite implementation for the ZhouChenbo88 submission package, managing tutors, students, weekly tutor availability and tutoring sessions. It is AI-assisted work prepared for the member to review, run and explain. The authenticated ZhouShenbo88 account has published the repository; the published Git commit author is ZhouShenbo88 after an authorized history rewrite. The project remains AI-assisted, so commit attribution alone does not establish independent human authorship.

## Submission and account status

The user requested individual implementations for three group members. This directory holds the independent Flask version assigned to ZhouChenbo88. The public repository was created and populated using the authenticated ZhouShenbo88 account. The `main` branch and actual story branch `codex/zhou-rg-core` were pushed. The rewritten integration commit is `d1cda9c2389c4f7fc283fd1b307e1b1f99004cd9`; the verified code and CI baseline is `8a1306b91e823bcde15fad976aa25de5fbc888d9`. Earlier Codex-attributed SHAs were replaced; the source tree is unchanged except for a separate README edit on `main`. See `docs/PUBLICATION.md` for the verified scope and outstanding evidence.

Repository: [ZhouShenbo88/redgum-tutoring](https://github.com/ZhouShenbo88/redgum-tutoring), default branch `main`. Clone it and follow the instructions below. A fresh local Git clone passed 41 tests; this verifies a clean local checkout and is distinct from independently testing a download from GitHub. The remote `main` pytest workflow [run 37217105790](https://github.com/ZhouShenbo88/redgum-tutoring/actions/runs/37217105790) completed successfully for code baseline `8a1306b91e823bcde15fad976aa25de5fbc888d9`. Genuine human peer review, Jira updates and Confluence publication remain pending.

The prototype has no user authentication or authorization. Its tutor-specific view is selected by tutor ID; it is a demonstration filter, not proof of identity. Anyone who can access this prototype can view and change its records. Use fictional data only and keep it on localhost. Do not upload real student names, contact details or tutoring records. A deployment that serves real users requires authenticated roles and access control.

## Local setup

Use Python 3.12. From this directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m flask --app app:create_app run --host 127.0.0.1
```

Open http://127.0.0.1:5000. The SQLite file persists between application restarts. Do not delete it to reset data unless you intend to lose the stored records. Make a copy of the database before changing the schema or removing a deployment.

Student records require a name, school year 5–12 and a family contact. Sessions last 60 or 90 minutes and must fit within one tutor availability window. Subject compatibility and inactive-student booking refusal are implementation assumptions recorded in `HANDOVER.md`. Overlap/double-booking detection remains outside the requested scope.

Run the automated checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The test suite uses a temporary database per test. The fresh local clone of the pre-rewrite, source-equivalent tree passed **41 tests** using `python -m pytest -q` on 28 September 2026. The rewritten code baseline was separately validated by the linked GitHub Actions run. The final staged application also ran under Waitress in a real browser: student/tutor CRUD, rejection of an out-of-window session and acceptance of a valid booking succeeded. Day/week schedules and student history views are implemented. Remote pytest CI succeeded in the linked run. These results do not verify a container build/recovery, production readiness or another person's acceptance review.

## Container demonstration

The container binds port 8080 and stores its database under `/data`. Supply a randomly generated secret and a persistent volume:

```powershell
docker build -t redgum-baseline .
docker volume create redgum-data
docker run --rm -p 127.0.0.1:8080:8080 -v redgum-data:/data -e SECRET_KEY=YOUR_RANDOM_SECRET redgum-baseline
```

Replace `YOUR_RANDOM_SECRET` before starting. Never commit a real secret or `.env` file. The production configuration deliberately fails when its secret is missing. The container remains a fictional-data demonstration until authentication and role permissions are implemented.

## Review before assessment

The intended member should review the requirement-to-feature mapping and the recorded local browser/test/remote CI results, explain the implementation, and check the filled RFP against the original brief. Report AI assistance according to the subject's requirements. Repository creation, the two branch pushes and the identified remote pytest run are completed facts. Human peer review and Jira/Confluence evidence remain outstanding; no client interview, public deployment or production acceptance is claimed.

