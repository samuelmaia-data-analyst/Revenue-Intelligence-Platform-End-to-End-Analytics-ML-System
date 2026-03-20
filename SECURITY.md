# Security Policy

## Supported Versions

Security fixes are applied on the default active development branch and through the latest repository state.

| Version | Supported |
| --- | --- |
| Latest | Yes |
| Older snapshots | No |

## Reporting A Vulnerability

Do not open public GitHub issues for suspected security vulnerabilities.

Report vulnerabilities privately through GitHub Security Advisories if enabled for the repository. If that path is not available, contact the maintainer directly and include:

- a concise summary of the issue
- affected files, components, or workflows
- reproduction steps or proof of concept
- severity and potential impact
- any suggested remediation

## Response Expectations

- initial triage target: within 5 business days
- remediation target: based on severity and exploitability
- coordinated disclosure preferred after a fix or mitigation is available

## Scope

Relevant security topics for this repository include:

- dependency vulnerabilities in Python and GitHub Actions
- unsafe handling of local artifacts or generated datasets
- secrets committed to the repository
- command execution paths exposed through automation or CLI workflows
