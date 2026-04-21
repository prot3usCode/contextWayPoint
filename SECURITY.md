# Security Policy

## Reporting

If you discover a vulnerability or a security concern in `contextWayPoint`,
please report it privately to the maintainer before opening a public issue.

For now, this repository does not publish a dedicated security mailbox. Use the
maintainer contact method associated with the repository and include:

- a short summary of the issue
- the affected files or commands
- reproduction steps
- the potential impact

## Scope

The current project is a local developer tool. The main security-sensitive areas
are:

- parsing authored YAML files
- writing compiled JSON and routed packet output
- future CLI or API integrations

## Expectations

- Do not open public issues with exploit details before the maintainer has time
  to review them.
- Prefer minimal reproduction cases that make the problem easy to verify.
- If the issue depends on a third-party package, include the package name and
  version when possible.
