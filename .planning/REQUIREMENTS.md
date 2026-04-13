# Requirements: longueuil-aweille Portfolio Polish

**Defined:** 2026-04-13
**Core Value:** A polished, well-tested CLI tool that demonstrates real-world Python engineering for recruiters

## v1 Requirements

### Bug Fixes

- [ ] **BUG-01**: Fix broken test referencing non-existent `ACTIVITY_NOT_FOUND` enum in `test_bot.py:56`
- [ ] **BUG-02**: Fix `_submit()` returning SUCCESS as default fallthrough — should return FAILED when no known status string is found (`registration.py:297`)
- [ ] **BUG-03**: Validate `activity_name` is non-empty before starting registration to prevent accidental random registration (`config.py:28-31`)

### Input Validation

- [ ] **VAL-01**: Add Pydantic validator for `carte_access` requiring exactly 14 digits with clear error message
- [ ] **VAL-02**: Add Pydantic validator for `telephone` requiring exactly 10 digits with clear error message
- [ ] **VAL-03**: Add Pydantic validator for `timeout` requiring positive integer (`gt=0`)
- [ ] **VAL-04**: Add Pydantic validator for `refresh_interval` requiring positive float (`gt=0.0`)

### Credential Security

- [ ] **SEC-01**: Mask `carte_access` in CLI output — show only last 4 digits (e.g., `****6489`) in `__main__.py:192`
- [ ] **SEC-02**: Create `config.example.toml` with placeholder values to guide users safely

### Architecture — Shared Navigation

- [ ] **ARCH-01**: Extract shared navigation logic from `registration.py:111-141` and `browse.py:104-142` into a shared `navigation.py` module
- [ ] **ARCH-02**: Consolidate duplicate selectors from 3 separate dataclasses into a single `selectors.py` module
- [ ] **ARCH-03**: Remove unused `ActivityInfo` dataclass from `registration.py:20-27`

### Reliability

- [ ] **REL-01**: Replace `wait_for_timeout()` sleeps with proper Playwright auto-waits (`wait_for_selector`, `wait_for_load_state`) across all bot modules
- [ ] **REL-02**: Add retry logic (3 attempts with backoff) for `page.goto()` calls to handle transient network failures
- [ ] **REL-03**: Use more specific element locators in `_submit()` instead of fragile full-page text matching

### Testing

- [ ] **TEST-01**: Add unit tests for `filter_activities()` in `browse.py` — cover day matching, age filtering, name filtering
- [ ] **TEST-02**: Add unit tests for `get_status_from_image_src()` in `status.py` — cover all branches
- [ ] **TEST-03**: Add unit tests for `Settings.from_toml()` — valid TOML, missing fields, malformed input
- [ ] **TEST-04**: Add Playwright mock route integration tests simulating the real site's HTML responses
- [ ] **TEST-05**: Add a coverage threshold (60%) enforced in CI via `--cov-fail-under`

### README & Presentation

- [ ] **PRES-01**: Add CI status badge, coverage badge, and Python version badge to README
- [ ] **PRES-02**: Add CLI demo screenshots or GIF showing register, verify, and browse commands in action
- [ ] **PRES-03**: Update README to reference `config.example.toml` instead of showing inline config

## v2 Requirements

### Logging

- **LOG-01**: Add file logging with rotation for audit trail of registration attempts

### Features

- **FEAT-01**: Add `--dry-run` flag that navigates and finds activity but stops before committing
- **FEAT-02**: Add `--schedule` option to start bot at a specific datetime

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multi-activity registration | Significant architecture change, low ROI for portfolio |
| Notification system (email/webhook) | Adds external dependencies, not core to demo |
| Scheduling support | Can be documented as "use cron", not worth building |
| Anti-bot detection handling | Target site doesn't use it, speculative feature |
| Docker/containerization | CLI tool, runs locally, no deployment target |
| Credential encryption at rest | Overkill for a local TOML file |
| Custom exception hierarchy | Nice-to-have but not recruiter-visible |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BUG-01 | Phase 1 | Pending |
| BUG-02 | Phase 1 | Pending |
| BUG-03 | Phase 1 | Pending |
| VAL-01 | Phase 1 | Pending |
| VAL-02 | Phase 1 | Pending |
| VAL-03 | Phase 1 | Pending |
| VAL-04 | Phase 1 | Pending |
| SEC-01 | Phase 1 | Pending |
| SEC-02 | Phase 1 | Pending |
| ARCH-01 | Phase 2 | Pending |
| ARCH-02 | Phase 2 | Pending |
| ARCH-03 | Phase 2 | Pending |
| REL-01 | Phase 3 | Pending |
| REL-02 | Phase 3 | Pending |
| REL-03 | Phase 3 | Pending |
| TEST-01 | Phase 4 | Pending |
| TEST-02 | Phase 4 | Pending |
| TEST-03 | Phase 4 | Pending |
| TEST-04 | Phase 4 | Pending |
| TEST-05 | Phase 4 | Pending |
| PRES-01 | Phase 5 | Pending |
| PRES-02 | Phase 5 | Pending |
| PRES-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-13*
*Last updated: 2026-04-13 after initial definition*
