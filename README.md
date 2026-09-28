# Redgum Tutoring — ZhouShenbo88 Flask version

A standalone Flask and SQLite implementation for the ZhouShenbo88 submission package, managing tutors, students, weekly tutor availability and tutoring sessions. It is an AI-assisted implementation prepared for review, execution and explanation by its intended member. This package does not establish that the account owner personally wrote the code or committed it to GitHub.

## Submission and account status


The planned repository URL is `https://github.com/ZhouShenbo88/redgum-tutoring`, with planned default branch `main`. This URL is a target, not a verified existing repository. After the owner authorizes publication and uploads the files, clone that repository and run the instructions below.

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

The test suite uses a temporary database per test. Local passing tests are distinct from a successful GitHub Actions run. Record the real command, result and date in the group's evidence; do not substitute an invented CI screenshot.

## Container demonstration

The container binds port 8080 and stores its database under `/data`. Supply a randomly generated secret and a persistent volume:

```powershell
docker build -t redgum-baseline .
docker volume create redgum-data
docker run --rm -p 127.0.0.1:8080:8080 -v redgum-data:/data -e SECRET_KEY=YOUR_RANDOM_SECRET redgum-baseline
```

Replace `YOUR_RANDOM_SECRET` before starting. Never commit a real secret or `.env` file. The production configuration deliberately fails when its secret is missing. The container remains a fictional-data demonstration until authentication and role permissions are implemented.

## Review before assessment

The intended member should review the requirement-to-feature mapping, run the program and tests, explain the implementation, and check the filled RFP against the original brief. Record real work after the repository and account permissions are confirmed. Report AI assistance according to the subject's requirements. Treat user interviews, usability results, deployment and GitHub activity as future work unless they have actually been performed.

