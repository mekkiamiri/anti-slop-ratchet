# Proposal (English)

**Format:** Tools-in-Action (30 min) · **Track:** Methodology & development practices (not the AI track, where it would be one of thirty) · **Level:** Intermediate

## Title (47 characters)

My Agent Wasn't Cheating. My Harness Was Blind.

## Abstract

I turned 11 recurring code-review comments into rules that block my coding agent: its harness. Over 180 ordinary tasks, they never fired once. Clean code, or blind sensors? Birgitta Böckeler asks the question and leaves it open.

I measured both answers. Is the agent cheating? 12 tickets that demand what a rule forbids, 144 runs, two models: zero bypasses; the agent quotes the rule and hands the decision back to you. Are the rules blind? Of 20 realistic defects injected into its code, they caught none, PMD and SpotBugs 4, the tests 3: 13 went unnoticed.

You leave with: a method to measure your harness by injecting defects, as mutation testing does for tests; one sentence that gives the agent a right to give up (cost ÷2.2); a check that fails on an empty diff. Everything is in a public repo, raw data included.

## Notes for the committee

- **Not the "ArchUnit guardrails for AI code" talk.** That talk has been given (Devoxx BE 2026). Here the rules are one slide; the subject is measuring the harness itself, answering a question Böckeler left open ("We need a way to evaluate harness coverage … similar to what code coverage and mutation testing do for tests", martinfowler.com, 2 April 2026).
- **A result against my own expectation**: I expected the agent to game the rules (as ImpossibleBench shows models do with tests); in 144 runs it never did. The real gap was elsewhere: the rules watch yesterday's mistakes.
- **Every number comes from the public repo** (github.com/mekkiamiri/anti-slop-ratchet, `mesures/`): three campaigns run in November 2026 (180, 144 and 50 agent runs), with raw JSONL, classifier, defect injector and replay commands; 31 runs checked by hand. Slides online: mekkiamiri.github.io/anti-slop-ratchet/slides/
- **Limits are said on stage**: one small Java project (414 lines), two models (November 2026), a code review played by an agent (not a human), 20 defects chosen by the speaker outside the 11 forms the rules target. What does not depend on those choices: no rule fired on any of the 50 runs, and none caught the 8 defects that are close cousins of a rule.
- **Demo**: the real transcript of the agent pleading, and one injected defect replayed live with the repo's injector (`injecter.py`), on a copy rebuilt from the published diff (`git apply`); recorded video as plan B.
- **Timing (30 min)**: 0-5:30 the harness and the silence · 5:30-14:30 hypothesis 1, cheating (refuted) · 14:30-25 hypothesis 2, blindness (confirmed) · 25-30 three gestures, limits, repo.
- **Speaker experience**: [to be completed by Mekki: meetups, JUG, video link]. Adaptable to a 15-min Quickie (hypothesis 2 only).

## Bio

Mekki Amiri is a Tech Lead and system architect, and the AI referent of a software development centre. He has practised software craftsmanship for 18 years (DDD, TDD, BDD) and now spends his time measuring what coding agents really do, rather than what we fear they do. He has proposed contributions to Google ADK Java, Spring AI A2A and AG-UI.
