# longueuil-aweille

## What This Is

A Python CLI tool that automates activity registration on the City of Longueuil recreation website using Playwright browser automation. Built for Quebec parents who need to compete for limited municipal activity spots that vanish in seconds. Published on GitHub as a portfolio piece for potential employers and recruiters.

## Core Value

A polished, well-tested, well-documented CLI tool that demonstrates real-world Python engineering — async patterns, browser automation, clean architecture, and thorough testing — that a recruiter can clone, understand, and run in minutes.

## Requirements

### Validated

<!-- Inferred from existing codebase -->

- ✓ Load configuration from TOML files with env var overrides — existing
- ✓ Auto-register for municipal activities via browser automation — existing
- ✓ Verify participant credentials against the Longueuil site — existing
- ✓ Browse available activities with filtering (domain, availability, age, day, location) — existing
- ✓ Multiple participant support — existing
- ✓ Auto-retry polling when registration is not yet open — existing
- ✓ CLI with rich-formatted output (panels, tables, colors) — existing
- ✓ Programmatic API for direct Python usage — existing
- ✓ CI pipeline (lint, typecheck, test) via GitHub Actions — existing
- ✓ Pre-commit hooks (ruff format, ruff check) — existing
- ✓ Strict mypy type checking — existing

### Active

- [ ] Fix broken test (ACTIVITY_NOT_FOUND enum mismatch in test_bot.py)
- [ ] Add input validation for carte_acces (14 digits) and telephone (10 digits)
- [ ] Mask credentials in CLI output (show last 4 digits only)
- [ ] Create config.example.toml with placeholder values
- [ ] Extract shared navigation logic from registration.py and browse.py
- [ ] Centralize selectors into a single shared module
- [ ] Replace wait_for_timeout() sleeps with proper Playwright auto-waits
- [ ] Fix _submit() default fallthrough (return FAILED, not SUCCESS)
- [ ] Add tests for pure functions: filter_activities(), get_status_from_image_src(), Settings.from_toml()
- [ ] Add Playwright mock route integration tests
- [ ] Enforce coverage threshold in CI
- [ ] Add README badges (CI status, coverage, Python versions)
- [ ] Add CLI demo screenshots/GIF to README
- [ ] Add shared navigation helper or SiteNavigator class
- [ ] Validate activity_name is non-empty before registration
- [ ] Add retry logic for transient network failures on page.goto()

### Out of Scope

- Multi-activity registration in a single run — significant architecture change, low ROI for portfolio
- Notification system (email/webhook) — adds external dependencies, not core to demo
- Scheduling support — can be documented as "use cron", not worth building
- Anti-bot detection handling — the target site doesn't use it, speculative feature
- Docker/containerization — CLI tool, runs locally, no deployment target
- Encryption of credentials at rest — overkill for a local TOML file

## Context

- **Brownfield project**: Working codebase with 7 source modules, 3 test files, CI pipeline
- **Target audience for portfolio**: Technical recruiters, engineering managers — they'll look at code quality, test coverage, README polish, and architecture decisions
- **Existing codebase map**: See `.planning/codebase/` for detailed analysis (ARCHITECTURE.md, CONCERNS.md, TESTING.md, etc.)
- **Known issues**: 22+ sleep-based waits, broken test, duplicate navigation logic, fragile ASP.NET selectors, default SUCCESS fallthrough
- **Recruiters typically evaluate**: README first impression, code organization, test quality, type safety, CI green status

## Constraints

- **Python**: 3.11+ required (stdlib tomllib dependency)
- **Target site**: ASP.NET WebForms site with auto-generated IDs — selectors are inherently fragile
- **No external services**: Must remain a standalone CLI tool, no databases or servers
- **Existing patterns**: Maintain Pydantic settings, Typer CLI, Rich output — don't rewrite the stack
- **Tests must pass**: CI must be green — this is the #1 signal for recruiters

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep Playwright (not requests/selenium) | Already working, async, modern, good for portfolio | — Pending |
| Centralize selectors into shared module | Reduces duplication across 3 bot files | — Pending |
| Use Playwright mock routes for integration tests | Tests real selector logic without hitting live site | — Pending |
| Replace sleeps with auto-waits | More reliable, demonstrates Playwright best practices | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-13 after initialization*
