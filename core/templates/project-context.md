# Project Context: <project-name>

<!-- TEMPLATE COMMENT
What this template is for: compact, durable context that describes one project under projects/<name>/.
When to update it: when the tech stack changes, when the architecture shifts, when new integrations are
added, or when the project's purpose changes materially. Do not update it after every sprint — only when
the information would mislead an AI tool reading it cold.
What files reference it:
  - adapters/claude-code/CLAUDE.md.template  (listed in "Read Before Acting")
  - adapters/codex/AGENTS.md.template        (listed in project context pointer)
  - core/skills/idea-to-prepared-task/SKILL.md (listed in Inputs)
Install: copy this file to projects/<name>/PROJECT_CONTEXT.md and fill in every placeholder.
-->

## What This Project Is

<One sentence stating the project's purpose. One sentence describing who uses it — internal team,
external customers, automated pipeline, etc. One sentence listing the main systems it integrates with.>

## Tech Stack

- **Language:** <primary language and version>
- **Framework:** <framework name and version, or "none">
- **Runtime:** <runtime environment — e.g., Node 20, Python 3.12, JVM 21>
- **Key libraries:** <comma-separated list of the three to five most important libraries>
- **Datastore:** <database or storage system, or "none">
- **Deployment target:** <where it runs — e.g., local CLI, containerised service, serverless function>

## Architecture (One Paragraph)

<Describe the system in one paragraph. Cover the main layers or modules, how data flows between them,
and any architectural constraints the project enforces. One paragraph maximum; if more is needed, the
architecture is not yet understood well enough to summarise, which is itself a risk worth noting in
RISKS.md.>

## Where Things Live (Codemap Pointer)

The authoritative file and module map is at `projects/<name>/CODEMAP.md`. Read it before scanning
the repository. If it is stale or absent, that is a higher-priority fix than the task at hand.

## Verification Commands

- **Build:** `<command to compile or bundle>`
- **Test:** `<command to run the full test suite>`
- **Lint:** `<command to run the linter>`
- **Run locally:** `<command to start a local instance>`

If verification steps require environment setup, see `projects/<name>/VERIFY.md` for the full procedure.

## AI Policy Pointers

- Permitted and restricted actions for AI tools: `projects/<name>/AI_POLICY.md`
- Project-specific maintainability rules: `projects/<name>/MAINTAINABILITY_NOTES.md`

## Known Risks

Active risks, mitigations, and owners are tracked at `projects/<name>/RISKS.md`. Read it before
proposing changes to high-risk areas.

## Decisions Log

Architectural and process decisions with rationale are at `projects/<name>/DECISIONS.md`. Check it
before proposing a change that might already have been considered and rejected.

---

## Example (Filled In)

```
# Project Context: log-analyzer

## What This Project Is
An internal CLI tool that parses structured log files and produces summary reports for the
infrastructure team. Used by on-call engineers to triage incidents. Integrates with the shared
object store for reading log archives and the alerting service for posting digests.

## Tech Stack
- Language: Go 1.22
- Framework: none
- Runtime: local binary, Linux x86-64
- Key libraries: cobra (CLI), zerolog (structured logging), testify (assertions)
- Datastore: local filesystem; reads from S3-compatible object store
- Deployment target: developer workstation and CI runner

## Architecture (One Paragraph)
Three layers: a parser that converts raw log lines into typed events, an aggregator that
groups events by severity and time window, and a reporter that writes the summary to stdout
or a file. No shared state between layers; each receives its input as a value and returns a
new value. Errors bubble up through explicit return values; no panics in production paths.
```
