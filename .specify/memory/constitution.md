<!--
Sync Impact Report
Version change: (none) -> 1.0.0
Modified principles: (initial creation)
Added sections: Core Principles; Architecture & Technical Constraints; Development Workflow & Quality Gates; Governance
Removed sections: None
Templates requiring updates:
	.specify/templates/plan-template.md ✅ (Constitution Check gates inserted)
	.specify/templates/spec-template.md ✅ (No direct changes needed; aligns)
	.specify/templates/tasks-template.md ✅ (Clarified E2E vs unit emphasis)
	.specify/templates/commands/* (directory absent) ⚠ (No action possible)
Deferred TODOs: None (initial ratification assumes today as ratification date)
-->

# ras-hunter Constitution

## Core Principles

### I. Simplicity First
Rules:
- Deliver the smallest feature slice that provides real user value.
- Minimize moving parts: prefer a functional core with a thin imperative shell.
- Introduce a new dependency ONLY if it removes ≥1 meaningful maintenance risk or ≥2 duplicated code blocks.
- Eliminate accidental complexity before adding capability.
Rationale: Smaller conceptual surface lowers defect rate, accelerates onboarding, and enables confident refactors.

### II. Explicit Over Implicit
Rules:
- All module boundaries MUST declare clear inputs, outputs, and side effects.
- No hidden global mutable state; configuration passed explicitly (or via a single well-defined config object at program start).
- Data transformations expressed as pure functions where feasible.
- Error paths are explicit: return Result/Either pattern or raise with contextual metadata.
Rationale: Explicit data flow is testable, predictable, and resistant to regression.

### III. High-Value End-to-End & Contract Tests
Rules:
- Each user journey (primary and error) MUST have an executable end-to-end test once implemented.
- Public contracts (CLI, API, file formats) MUST have contract tests asserting schema, status, and representative edge cases.
- Unit tests are reserved for complex pure logic (algorithms, parsing, domain calculations) — avoid trivial assertion churn.
- A failing high-level test MUST precede implementation of new externally observable behavior.
Rationale: E2E + contract tests maximize defect detection per line of test code and protect real user value; selective unit tests keep signal high.

### IV. Fail Fast with Diagnostic Errors
Rules:
- Any error surfaced to logs/stderr MUST include: operation name, sanitized key inputs, expected vs actual (when applicable), and a stable error code/tag.
- Avoid silent retries; implement bounded retries with explicit logging of attempt counts.
- Prefer structured logging (JSON or key=value) for machine parsing; human summary stays concise.
- Never swallow exceptions without adding context; rethrow with original cause preserved.
Rationale: Rich, structured context cuts mean-time-to-diagnose and prevents repeated unknown failure modes.

### V. Incremental Evolution & Backward Safety
Rules:
- Default stance: maintain backward compatibility for external contracts; if a break is unavoidable, a migration note + version bump plan MUST be documented before merge.
- Semantic Versioning: MAJOR=breaking change to public contract; MINOR=new capability (non-breaking); PATCH=internal change or clarification.
- Refactors proceed in small, reviewable steps; large rewrites require an explicit risk/benefit note.
- Dead code is removed promptly once no longer referenced (verified by search + tests).
Rationale: Predictable evolution sustains velocity while preserving user trust.

## Architecture & Technical Constraints

- Core logic implemented as pure functions where possible; side effects (I/O, network, filesystem, environment) isolated at boundaries.
- No implicit singletons; explicit construction + dependency injection (simple manual wiring preferred over frameworks until justified).
- Logging and error handling live at edges; domain code returns values or structured errors.
- Data passed across boundaries uses stable, versioned schemas (document changes in spec/ or contracts/ when introduced).
- Limit concurrency primitives to the simplest primitive that works (e.g., queue > thread pool > custom scheduler).
- Performance work is driven by measured bottlenecks (add a profiling note in plan.md before significant tuning).

## Development Workflow & Quality Gates

1. Specify: Create or update spec (user stories + acceptance + success criteria).
2. Plan: Fill implementation plan; Constitution Check MUST pass before coding.
3. Test First (High-Level): Add/extend an E2E or contract test that fails for new behavior.
4. Implement Minimal Pass: Write just enough code to satisfy failing test.
5. Refactor: Remove duplication, enforce principles (simplicity, explicitness).
6. Extend Selective Unit Tests: Only for complex logic not fully covered by E2E.
7. Review Gate (Checklist):
	 - Simplicity: Any new dependency or abstraction justified inline.
	 - Explicitness: Inputs/outputs documented (code or docstring).
	 - E2E Coverage: New journey or contract change has a corresponding test.
	 - Errors: Added/changed error paths include diagnostic context.
	 - Evolution: Breaking change? If yes, version bump + migration note.
8. Merge only when all gates satisfied; otherwise update plan or spec before retry.

Quality Gates Automation (future enhancement ideas):
- Lint rule for forbidden hidden globals.
- Script to detect unreferenced files (dead code candidate list).
- Contract test harness to diff schemas.

## Governance

Authority & Scope:
- This constitution supersedes ad-hoc conventions. Conflicts resolved in favor of the latest ratified version.

Amendments:
- Proposal via PR modifying this file + Sync Impact Report update.
- REQUIRED for approval: (a) Rationale section, (b) Version bump justification, (c) Migration notes if breaking.
- At least one maintainer other than proposer MUST approve.

Versioning Policy:
- MAJOR: Removal or incompatible redefinition of a public contract principle or workflow gate.
- MINOR: Addition of a new principle or meaningful expansion of existing rule set.
- PATCH: Clarifications, grammar, non-semantic tightening.

Compliance & Review:
- Quarterly (or sooner if >3 MINOR bumps) audit: sample PRs checked against principles.
- Non-compliance triggers: Add task to remediate + possible PATCH clarification.

Documentation Sync:
- plan-template.md lists automated Constitution Check gates.
- tasks-template.md clarifies E2E/contract priority over exhaustive unit tests.
- spec-template.md already structured to encourage independently testable stories.

Breaking Change Procedure:
1. Open issue describing impact + alternatives considered.
2. Add migration instructions to README or contracts/.
3. Bump version per policy in same PR as change.

**Version**: 1.0.0 | **Ratified**: 2025-10-24 | **Last Amended**: 2025-10-24
