# Testing Policy

## Default Rule

Default tests must not use real network access.

Any test that runs during normal local validation, CI, or handoff completion must use local fixtures, mocks, or temporary local files.

## Live Test Rule

Live tests are allowed only when all conditions are true:

- the test is explicitly marked as live
- the test is skipped by default
- an environment variable enables it
- the assigned handoff permits it

Suggested environment variable:

`QUANT_SYSTEM_LIVE_TESTS=1`

For any task that implements a real source adapter or real data-fetching behavior, a gated live smoke test is mandatory. It still must be skipped by default and must only run when the handoff explicitly permits it.

## Live Network Failure Rule

When a live-enabled smoke test fails or skips because of network, proxy, DNS, TCP/TLS, upstream, or public-source availability, treat it as a reviewable task blocker unless the active handoff explicitly says the external skip is acceptable evidence for that task.

Required handling:

- Controller dispatches a 5.3 execution rework instead of closing the task directly.
- Execution diagnoses the failure and changes allowed code/tests/report where a repository-level fix is feasible.
- Execution records the live-enabled result truthfully as PASS, SKIP, or FAIL.
- Execution includes root-cause evidence, such as proxy environment redaction, DNS/TCP/TLS behavior, source endpoint attribution, and whether the issue is repository-fixable.
- Review Agent independently reviews the rework before the task can be accepted.
- Integration Agent integrates only after an accepted review.

An external environment/source skip may remain a skip only when the report explains why no repository-level fix is feasible and gives a concrete operator action.

## Data Source Credentials

No credential is allowed in source control.

Credentials must come from environment variables, local ignored config files, or system keychains in a future approved design.

## Fixture Policy

Fixtures should be:

- small
- deterministic
- locally committed when safe
- stripped of private account data
- documented enough to explain their source or synthetic nature

## Test Categories

| Category | Network | Default | Purpose |
| --- | --- | --- | --- |
| unit | no | yes | pure logic and schema checks |
| integration_offline | no | yes | local file and storage behavior |
| contract | no | yes | DataHub output schema compatibility |
| live_source | yes | no | mandatory gated smoke checks for real-source adapter or real data-fetching tasks |

## Handoff Requirements

Every execution handoff must state:

- which tests to run
- whether live tests are forbidden or allowed
- which environment variable controls live behavior
- how live-enabled network/source failures should be diagnosed and reported when the task touches real data sources

If a handoff is silent about live tests, live tests are forbidden.
