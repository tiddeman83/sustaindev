# Service Catalog: <project-name>

<!--
TEMPLATE COMMENT

What this template is for:
  A canonical list of every service interface in the project, with the public
  method signatures the AI tool needs to know to route work correctly. Without
  this, AI tools that prepare briefs (or that suggest implementations) will
  guess at interface shapes — and case-study-03 in the SustainDev public repo
  documents how that produces architectural mismatches that cost meaningful
  rework when caught at execution time.

When to update it:
  When a service interface gains, loses, or renames a public method.
  When a service is added, removed, or its responsibility shifts.
  Not on every commit — only when the catalog would mislead a reader.

What references it:
  - PROJECT_CONTEXT.md should mention that the catalog exists and where it
    lives.
  - core/skills/idea-to-prepared-task/SKILL.md (in SustainDev) lists this as
    optional input that the prep step can include in its context bundle.
  - scripts/schedule/prepare-task.py can load it when present (planned for
    SustainDev v0.2).

Install:
  copy this file to <project-root>/SERVICE_CATALOG.md and fill it in.
  Or have a local model draft it from the project's interface files
  using scripts/sprint1/draft-catalog.py — see case-study-05.md for what
  to expect from that workflow.

Format choices encoded in this template:
  - Public methods are listed by signature, not by full XML doc-comment. The
    purpose line + method list is enough to route work; full docs are in the
    code.
  - Every service entry has a "responsibility" line that should be readable
    in 5 seconds. If yours takes longer, the service may be doing too much.
  - "Depends on" lists other catalog entries (or external libraries that
    matter to routing decisions). "Used by" lists callers — useful when the
    AI is asked "what would change if I touched this service?"
  - Keep the catalog under ~250 lines. Above that, split by layer or domain
    (e.g., SERVICE_CATALOG_CORE.md, SERVICE_CATALOG_UI.md).
-->

## Layer summary

A short paragraph describing the service-layer architecture in this project.
Mention the DI scope (singleton / scoped / transient), where services are
registered (one file? scattered?), the layer boundary (Core vs UI vs
infrastructure), and any architectural rules that govern what a service may
or may not do (e.g., "Services in the Core layer may not depend on UI
framework APIs").

---

## Services

### `<IServiceName>`

**File:** `<relative/path/to/IServiceName.cs>`
**Implementation:** `<relative/path/to/ServiceName.cs>` (and `<NullServiceName.cs>` if Null Object pattern).
**DI scope:** singleton / scoped / transient
**Responsibility:** One sentence. What this service is the source of truth for.

**Public methods:**

```text
<Type> MethodName(<ArgType> argName, ...)
<Type> AnotherMethod(...)
```

**Depends on:** `<IOtherService>`, `<external-library>`, or "none".
**Used by:** `<CallerViewModel>`, `<CallerService>`, or "registration-only".
**Notes:** Anything routing-relevant. Threading model, common pitfalls,
related risks in `RISKS.md`.

---

### `<INextService>`

(repeat the pattern for every service)

---

## Anti-services

If the project has classes that look like services but should not be added
here, list them with a one-line reason. Examples:

- `<SomeHelperClass>` — pure helper, no DI registration, no interface; should
  be classified as a static utility, not a service.
- `<SomeManagerClass>` — has been deprecated; new code routes through
  `<IReplacementService>` instead.

This section prevents AI tools from inferring "this looks like a service so
treat it like one."

---

## Last verified

Last verified: `<YYYY-MM-DD>` by `<person-or-tool>`.

If this date is more than a major release behind the current code, treat the
catalog as stale and prefer reading the actual interface files.

---

## Example (filled in)

The example below is sanitized — a generic CLI tool for log analysis with two
services. Real projects will be longer, but the shape is the same.

```text
# Service Catalog: logparse-cli

## Layer summary

Two services live in src/logparse/services/, both registered as singleton
in ServiceCollectionExtensions. Services may not depend on the CLI parsing
layer; the CLI calls services, not the other way around.

## Services

### `IParserService`

File:           src/logparse/services/IParserService.cs
Implementation: src/logparse/services/ParserService.cs
DI scope:       singleton
Responsibility: Parse raw log lines into typed events.

Public methods:

  IEnumerable<LogEvent> Parse(IEnumerable<string> lines)
  bool CanParse(string firstLine)

Depends on:     none (pure)
Used by:        ReporterService, CliParseCommand
Notes:          Stateless; safe to call from any thread.


### `IReporterService`

File:           src/logparse/services/IReporterService.cs
Implementation: src/logparse/services/ReporterService.cs
DI scope:       singleton
Responsibility: Aggregate parsed events and write a summary report.

Public methods:

  void WriteReport(IEnumerable<LogEvent> events, TextWriter output)
  ReportSummary Summarize(IEnumerable<LogEvent> events)

Depends on:     IParserService
Used by:        CliReportCommand
Notes:          Buffered output; call WriteReport in one shot, not per-event.


## Anti-services

- LineNormalizer — pure static helper; no interface, no DI.

## Last verified

Last verified: 2026-04-26 by maintainer.
```
