# Zhang publication and verification record

Implementation prepared on 28 September 2026; publication metadata and evidence refreshed on 5 October 2026. This separate Node application uses fictional records only. No private student numbers, real contact addresses, account tokens or login credentials are included in this evidence record.

## Published source and account

- Repository: [ZhouShenbo88/redgum-tutoring](https://github.com/ZhouShenbo88/redgum-tutoring).
- Zhang implementation: [zhangyanming branch](https://github.com/ZhouShenbo88/redgum-tutoring/tree/zhangyanming).
- Story branch pushed: [codex/zhang-rg-core](https://github.com/ZhouShenbo88/redgum-tutoring/tree/codex/zhang-rg-core).
- The **ZhangYanming88** collaborator invitation was accepted; publication used that authenticated collaborator account.
- Rewritten code/CI baseline: [`980e8a9540419a3c9c1204dde39fce29472e4793`](https://github.com/ZhouShenbo88/redgum-tutoring/commit/980e8a9540419a3c9c1204dde39fce29472e4793). The previous Codex-attributed SHAs were superseded by the authorized history rewrite; the source tree was preserved.

The published Git commit author is now **ZhangYanming88** after the user-authorized history rewrite. The work remains AI-assisted, and Git metadata cannot independently prove who wrote each line. The member must review, understand and disclose assistance as required by the unit.

## Actual verification

- Local Node v24.19.0 `node --test`: 24 tests passed, zero failures.
- A fresh local Git clone of the source-equivalent pre-rewrite `zhangyanming` branch passed all 24 tests with a clean working tree. The linked remote CI separately verifies the rewritten branch; the local clone is distinct from downloading the remote GitHub repository.
- Final staged browser verification saved fictional student and tutor records, rejected an invalid 18:30 one-hour booking that exceeded the tutor's window, and displayed a valid 16:00 session with booked status.
- [GitHub Actions run 37217130857](https://github.com/ZhouShenbo88/redgum-tutoring/actions/runs/37217130857) was verified successful for its Node 22 and Node 24 matrix. This is real remote CI evidence, separate from local test output.

The checks establish the identified behaviours and execution environments. Docker execution and production deployment have not been verified. The application continues to have no authentication and must use fictional data.

## Remaining case Definition of Done requirements

Another human team member's actual PR review with comments addressed, Jira acceptance-criterion demonstrations/status updates, and Confluence decisions/handover remain pending. Pushed branches and successful CI do not establish those separate activities. The six-section Markdown handover is preparation for the required Confluence publication; it is not evidence that Confluence was used.
