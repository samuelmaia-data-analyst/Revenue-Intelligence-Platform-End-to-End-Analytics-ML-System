# Documentation Map

This repository keeps documentation intentionally small and operational. Each document exists to help a reviewer or collaborator answer a concrete question quickly.

## Core Documents

- [architecture.md](architecture.md): system boundary, runtime path, data flow, reliability controls and trade-offs
- [repository_structure.md](repository_structure.md): why directories exist, where new code belongs and what should stay out of the top level
- [onboarding.md](onboarding.md): fastest path to a successful local run, validation commands and common failure modes
- [runbook.md](runbook.md): operational commands, failure investigation and output validation checklist
- [troubleshooting_matrix.md](troubleshooting_matrix.md): fast diagnosis map from symptom to artifact and first action
- [release_process.md](release_process.md): lightweight release discipline for technical portfolio changes
- [deprecation_policy.md](deprecation_policy.md): how compatibility shims are handled and eventually removed
- [merge_policy.md](merge_policy.md): labels, merge expectations, and what must be green before merging
- [adr/README.md](adr/README.md): short decision records for the most important architectural trade-offs
- [hiring_review.md](hiring_review.md): honest portfolio assessment from a hiring-review perspective

## Planning and Maintenance

- [staff_upgrade_master_issue.md](staff_upgrade_master_issue.md): tracked work for portfolio hardening and senior-level upgrades
- [issues](issues): issue templates and project-level backlog support
- [releases](releases): release-oriented documentation and changelog support
- [releases/v1.1.0.md](releases/v1.1.0.md): latest portfolio-hardening release summary
- [releases/v1.2.0.md](releases/v1.2.0.md): latest governance and downstream-validation release summary
- [releases/v1.3.0.md](releases/v1.3.0.md): dbt runtime hardening, localized docs updates, and container-level API validation
- [releases/v1.3.1.md](releases/v1.3.1.md): processed-exports smoke coverage, richer incident handling, and CI/runtime alignment

## Reading Order

1. Start with the root `README` in your preferred language.
2. Read [architecture.md](architecture.md) for the system model.
3. Read [runbook.md](runbook.md) to understand operation and recovery.
4. Read [troubleshooting_matrix.md](troubleshooting_matrix.md) for faster diagnosis.
5. Read [repository_structure.md](repository_structure.md) before moving files or adding modules.
6. Use [onboarding.md](onboarding.md) when you need to run, validate or extend the project locally.
