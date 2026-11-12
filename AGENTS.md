# Repository instructions

## Deferred CFG Audit follow-up (2026-11-12)

These maintenance items are deferred while the project is inactive. Review and resolve them when work resumes, before re-enabling the affected agent integrations.

- [ ] CFG123 — `venv/pyvenv.cfg`: remove the tracked `venv/` directory, ignore local virtual environments, and recreate them from the project's dependency declarations before running the project or agent tools.

Validation: run `npx cfgaudit@1.21.0 --config /dev/null --format json .` from the repository root. Record completed fixes here; informational findings may remain when the integration is intentional and its review is documented.
