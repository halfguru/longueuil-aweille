# Roadmap: longueuil-aweille Portfolio Polish

## Overview

Polish a working Longueuil activity registration CLI tool into a recruiter-ready portfolio piece. Start by fixing bugs and hardening input validation, then clean up duplicated architecture, improve browser automation reliability, build comprehensive test coverage, and finish with a README that makes a strong first impression.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Fix & Harden** - Fix broken tests, add input validation, secure credential display
- [ ] **Phase 2: Clean Architecture** - Extract shared navigation, consolidate selectors, remove dead code
- [ ] **Phase 3: Reliability** - Replace sleep-based waits with proper Playwright primitives, add retry logic
- [ ] **Phase 4: Test Coverage** - Unit tests for pure functions, mock-route integration tests, CI coverage gate
- [ ] **Phase 5: README & Presentation** - Badges, CLI demo visuals, polished config documentation

## Phase Details

### Phase 1: Fix & Harden
**Goal**: The tool rejects invalid input with clear errors, masks credentials in output, and has zero broken tests
**Depends on**: Nothing (first phase)
**Requirements**: BUG-01, BUG-02, BUG-03, VAL-01, VAL-02, VAL-03, VAL-04, SEC-01, SEC-02
**Success Criteria** (what must be TRUE):
  1. `uv run pytest` produces 0 failures — the broken ACTIVITY_NOT_FOUND test is fixed and `_submit()` returns FAILED on unknown status
  2. Invalid inputs (wrong-length carte_acces, wrong-length telephone, non-positive timeout, non-positive refresh_interval) produce clear Pydantic validation errors before any browser interaction
  3. Empty activity_name is rejected with a validation error before registration begins
  4. CLI output shows only the last 4 digits of carte_acces (e.g., `****6489`)
  5. `config.example.toml` exists with documented placeholder values and instructions
**Plans**: TBD

### Phase 2: Clean Architecture
**Goal**: Navigation and selectors are centralized, eliminating duplication across bot modules
**Depends on**: Phase 1
**Requirements**: ARCH-01, ARCH-02, ARCH-03
**Success Criteria** (what must be TRUE):
  1. Both registration.py and browse.py import navigation helpers from a shared module — no duplicate navigation code
  2. All CSS selectors live in a single `selectors.py` module referenced by all bot modules
  3. The unused `ActivityInfo` dataclass is removed from the codebase
  4. Existing registration and browse flows work identically after refactoring (no behavior change)
**Plans**: TBD

### Phase 3: Reliability
**Goal**: The bot handles flaky network conditions and page loads without brittle sleep-based waits
**Depends on**: Phase 2
**Requirements**: REL-01, REL-02, REL-03
**Success Criteria** (what must be TRUE):
  1. No `wait_for_timeout()` calls remain in bot modules — all waits use Playwright auto-wait primitives (`wait_for_selector`, `wait_for_load_state`)
  2. Transient network failures on `page.goto()` are retried automatically up to 3 times with backoff
  3. `_submit()` uses specific element locators instead of fragile full-page text matching
**Plans**: TBD

### Phase 4: Test Coverage
**Goal**: The test suite covers pure functions and critical browser flows with a CI-enforced threshold
**Depends on**: Phase 2
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04, TEST-05
**Success Criteria** (what must be TRUE):
  1. `filter_activities()` has tests covering day matching, age filtering, and name filtering
  2. `get_status_from_image_src()` has tests covering all status branches
  3. `Settings.from_toml()` has tests for valid input, missing fields, and malformed input
  4. Integration tests use Playwright mock routes to simulate the real site's HTML responses for registration and browse flows
  5. CI fails if coverage drops below 60% (`--cov-fail-under=60`)
**Plans**: TBD

### Phase 5: README & Presentation
**Goal**: A recruiter's first impression of the README shows a professional, well-maintained project
**Depends on**: Phase 4
**Requirements**: PRES-01, PRES-02, PRES-03
**Success Criteria** (what must be TRUE):
  1. README displays CI status, coverage, and Python version badges at the top
  2. README includes a CLI demo screenshot or GIF showing register, verify, and browse commands
  3. README references `config.example.toml` for setup instead of showing inline config
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Fix & Harden | 0/? | Not started | - |
| 2. Clean Architecture | 0/? | Not started | - |
| 3. Reliability | 0/? | Not started | - |
| 4. Test Coverage | 0/? | Not started | - |
| 5. README & Presentation | 0/? | Not started | - |
