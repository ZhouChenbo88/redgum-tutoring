# Verified publication and local evidence

Implementation prepared on 28 September 2026; publication metadata and evidence refreshed on 5 October 2026.

- The public repository [ZhouShenbo88/redgum-tutoring](https://github.com/ZhouShenbo88/redgum-tutoring) was created and populated using the authenticated `ZhouShenbo88` account.
- Default branch `main` and actual story branch `codex/zhou-rg-core` were pushed.
- Rewritten integration commit: `d1cda9c2389c4f7fc283fd1b307e1b1f99004cd9`. Verified code/CI baseline: `8a1306b91e823bcde15fad976aa25de5fbc888d9`. The previous Codex-attributed SHAs were superseded by the authorized rewrite; the source tree was preserved, with a separate README edit retained on `main`.
- A fresh local Git clone of the source-equivalent pre-rewrite baseline passed 41 tests using `python -m pytest -q`. The linked remote CI separately verifies the rewritten code baseline; the local clone is not evidence of a clean GitHub download.
- Remote `main` pytest workflow [run 37217105790](https://github.com/ZhouShenbo88/redgum-tutoring/actions/runs/37217105790) completed successfully for code baseline `8a1306b91e823bcde15fad976aa25de5fbc888d9`. It installs the declared development requirements and runs pytest; it is not a container build or recovery test.
- The final staged application ran under Waitress and was exercised in a real browser. Student/tutor CRUD, rejection of an out-of-window session and acceptance of a valid booking succeeded. Day/week schedules and student history views are implemented.
- Published commits now show author `ZhouShenbo88` after the user-authorized history rewrite. That metadata does not prove the member independently wrote the AI-assisted code. The member must review, understand and disclose AI assistance according to unit requirements.

The identified remote pytest run is verified. Container build/restart/recovery, genuine human PR peer review, Jira issue/acceptance evidence and Confluence publication remain outstanding. No public application deployment, real client interview, supplier contract or production acceptance is asserted. No student number, real family contact or secret is included in this record.

`docs/LOCAL_GIT.md` summarizes the current source-provenance boundaries. The history rewrite did not create a human pull-request review or Jira/Confluence activity.
