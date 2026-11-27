# Proposal (English)

**Format:** Tools-in-Action (30 min) · **Track:** Development practices

## Title (≤ 70 characters)

My Agent Wasn't Cheating. My Harness Was Blind.

## Abstract

I turned 11 recurring code-review comments into deterministic rules that block my coding agent. Over 180 ordinary tasks, they never fired once. Birgitta Böckeler asks the open question: when sensors never fire, is it quality, or blindness?

I measured both answers. Cheating? 12 tickets that cannot be done without breaking a rule, 144 runs, two models: zero bypasses. The agent quotes the rule and asks you to decide. Blindness? A senior-style review of 10 agent diffs gave 38 comments: the rules saw 0. Of 20 injected realistic defects, the rules caught 0, PMD and SpotBugs 4, the tests 3. Thirteen went unnoticed.

You leave with three cheap gestures: give the agent a right to give up (one sentence: cost ÷2.2), measure your harness coverage by injecting defects, and fail on an empty diff. Everything is in a public repo, raw data included.

## Notes for the committee

- **Not the "ArchUnit guardrails for AI code" talk.** That talk has been given (Devoxx BE 2026). Here the rules are one slide; the subject is measuring the harness itself, answering a question Böckeler left open ("We need a way to evaluate harness coverage … similar to what code coverage and mutation testing do for tests", martinfowler.com, 2 April 2026).
- **Every number comes from the public repo** (`mesures/`): three campaigns run in November 2026 (180, 144 and 50 agent runs), with raw JSONL, classifier, defect injector and replay commands. 31 runs were checked by hand.
- **The talk reports a result against my own expectation**: I expected the agent to game the rules (as ImpossibleBench shows models do with tests); it did not.
- **Limits are said on stage**: one small Java project (414 lines), two models, a simulated (not human) review, defects chosen by the speaker. The 0% of the rules does not depend on those choices.
- Demo: the real transcript of the agent pleading, and one injected defect replayed with the repo's injector (`injecter.py`).

## Bio

Mekki is a Tech Lead and system architect, and the AI referent of a software development centre. He has practised software craftsmanship for 18 years (DDD, TDD, BDD) and now spends his time measuring what coding agents really do, rather than what we fear they do. He has proposed contributions (open pull requests) to Google ADK Java, Spring AI A2A and AG-UI.
