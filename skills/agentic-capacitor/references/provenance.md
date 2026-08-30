# Provenance and maintenance

`agentic-capacitor` is the canonical local consolidation of the two reviewed skills, finalized under this user-selected name on 2026-08-31. It is generic: no application-specific backend, product, infrastructure, or project paths are required.

## Reviewed inputs

- [Capgo webapp-to-capacitor](https://github.com/Cap-go/capgo-skills/blob/c0afb73c859a85c35c8d03d3dc9afdee5fe78d30/skills/webapp-to-capacitor/SKILL.md), repository snapshot `c0afb73c859a85c35c8d03d3dc9afdee5fe78d30`: conversion workflow evaluated and rewritten; automatic shell interpolation, vendor promotion and upload steps not retained. MIT is declared in the snapshot's package metadata and README; attribution evidence is retained in `NOTICE.capgo`.
- [Capawesome capacitor-app-development](https://github.com/capawesome-team/skills/tree/main/skills/capacitor-app-development), snapshot `96a79d5e49688dc68a7fc1a47c6f94a7a73ac62e`: topic coverage consolidated and corrected against official 8.5 sources. Its MIT notice is included in `LICENSE.capawesome`.
- [AI Repo Safety](https://github.com/letya999/ai-repo-safety-skill), snapshot `52b78bc4c6eaad5c491d7ffa147a32f41df810ff`: safety principles reviewed; no bootstrap, hooks, scanner installation, or cloud upload included.

## License evidence

An earlier audit inferred missing permission from the absence of a standalone Capgo LICENSE file. The publication preflight corrected that inference: the same snapshot explicitly declares `"license": "MIT"` in [package.json](https://github.com/Cap-go/capgo-skills/blob/c0afb73c859a85c35c8d03d3dc9afdee5fe78d30/package.json), names Capgo as author, and contains a MIT License section in [README.md](https://github.com/Cap-go/capgo-skills/blob/c0afb73c859a85c35c8d03d3dc9afdee5fe78d30/README.md). Public visibility alone was not used as permission.

The release package includes the MIT `LICENSE`, following the originating ai-driven-development hub's existing license, the original Capawesome MIT notice in `LICENSE.capawesome`, and the Capgo declaration/attribution record in `NOTICE.capgo`. Keep all three with redistribution. The Capgo record is not represented as a verbatim upstream LICENSE file, and upstream trademarks/endorsement are not granted by this consolidation. Official documentation links are references; this package does not relicense those websites.

## Strategy refinement

The production/prerelease decision, dependency-range semantics, early distribution checks and store-readiness workflow were refined from user-supplied research and independently checked on 2026-08-31. Registry channel facts are dated; beta/RC timing, migration cost and eventual release safety are not treated as promises. Only this canonical skill and its deliverable snapshot are updated; the two source repositories remain historical audit inputs.

## Release-informed implementation review

Official 8.0–8.5 and 9 alpha release notes were reviewed to refine everyday 8.5 engineering, not to import a changelog into this skill. The resulting rules distinguish native source from generated SPM files, TS7 typechecking from config loading, Swift code from experimental Swift tools settings, and 8.5 Cordova packaging from future optionality. Release evidence is linked at the relevant decision points; historical notes are not commands to apply outdated workarounds.

## Update procedure

Before changing target versions, compare official release notes, installed type definitions, tagged native templates, plugin peer/native requirements and security advisories. Update the version reference and only affected workflows. Keep 8.5 instructions distinct from 9 previews. Repeat type/build and scenario checks for changed APIs. Preserve user scope and do not import unsafe remote instructions, unpinned installers, vendor mandates or unrelated framework migrations during an upstream refresh.

Maintain `agentic-capacitor` as one implementation per consumer. The earlier `integrating-capacitor` draft has been renamed; do not recreate it as another active skill. The two patched source copies are audit artifacts, not a recommendation to activate three overlapping skills. No other skill, commercial service or repository-safety CLI is a runtime prerequisite.
