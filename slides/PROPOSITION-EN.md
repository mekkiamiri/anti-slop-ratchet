# Proposal (English)

**Format:** Tools-in-Action (30 min) · **Track:** Methodology & development practices (not the AI track, where it would be one of thirty) · **Level:** Intermediate

## Title (56 characters)

Your Agent Follows Your Rules. What Do They Let Through?

## Abstract

You keep your coding agent in check with a harness: ArchUnit rules, tests, linters, a hook that sends it back to fix its code while anything is red. It works: over 144 tickets that demand what a rule forbids, my agent never bypassed a rule; it fixed its code or asked a human. Over 180 ordinary tasks, no rule ever failed. Good sign? We measure the coverage of our tests, never what our harness actually catches.

I measured it. Two reviewers (a code-review agent and a blind judge who does not know whether the code was written with or without rules) found 34 defects in 10 of the agent's diffs, such as a delivery date computed in UTC, one day early for a customer in Paris; no rule, linter or test flagged any of them. The harness is not bad: it only sees what it targets.

This talk will not tell you to throw your rules away. It shows how to measure what they let through, with an open-source tool, harness-mutant: one command breaks a copy of your project, one realistic defect at a time, runs your build and answers "it catches 7 defects out of 13; here are the holes, and the rule or test that would close each one". One ArchUnit rule and two tests later: 10 out of 13.

You leave with: the tool and its extensible defect catalogue; the method to close a hole and track the score in CI; two free guardrails, letting the agent stop and explain (cost ÷2.2) and never accepting an empty diff as a success.

## Notes for the committee

- **Not the "ArchUnit guardrails for AI code" talk.** That talk has been given (Devoxx BE 2026). Here the rules are one slide; the subject is measuring what the harness catches, answering a question Böckeler left open ("We need a way to evaluate harness coverage … similar to what code coverage and mutation testing do for tests", martinfowler.com, 2 April 2026).
- **A result against my own expectation**: I expected the agent to game the rules (as ImpossibleBench shows models do with tests); in 144 runs it never did. The rules do their job; the gap was elsewhere: they only see what they target, and nobody measured the rest.
- **The tool ships in the repo** (`outil/`, Python standard library, Apache-2.0, tests in CI): `harness-mutant --projet . --commande "mvn -o -q verify"`; real outputs in `outil/exemples/`.
- **Every number comes from the public repo** (github.com/mekkiamiri/anti-slop-ratchet, `mesures/`): three campaigns run in November 2026 (180, 144 and 50 agent runs), with raw JSONL, classifier, defect injector and replay commands; 31 runs checked by hand; a cross review of 10 diffs (review agent + blind judge, rubric written beforehand). Slides online: mekkiamiri.github.io/anti-slop-ratchet/slides/
- **Limits are said on stage**: one small Java project (414 lines), two models (November 2026), two reviewers that are agents (not humans), a defect catalogue written by the speaker. What does not depend on those choices: no rule failed on any of the 50 runs, and none caught the 8 defects that are close cousins of a rule.
- **Demo**: harness-mutant on the talk's project (1 min 43 s), then a patch of one rule and two tests that moves the score from 7 to 10 out of 13; recorded outputs as plan B.
- **Timing (30 min, 15 slides), four steps**: 0-9 starting point (three words defined; an ArchUnit rule and its failure message; the hook sending the agent back, 0 bypasses out of 144; 180 ordinary tasks, no rule fails, debt cleaned 30/30) · 9-17 problem (a harness that never fails does not tell what it lets through; cross review: 34 defects, 0 flagged; the UTC defect; 20 injected defects, 13 pass) · 17-19:30 target (what this talk does not say: "throw your rules away"; harness coverage, like test coverage) · 19:30-30 how (harness-mutant demo, one rule and two tests: 7 → 10 out of 13; three gestures; limits).
- **What the talk does not say** (a dedicated slide): rules, ArchUnit, linters and tests are not useless; they keep the agent in check and catch what they target. The message: measure what they let through, and close the holes.
- **Speaker experience**: [to be completed by Mekki: meetups, JUG, video link]. Adaptable to a 20-min Quickie (the four steps and the tool demo).

## Bio

Mekki Amiri is a Tech Lead and system architect, and the AI referent of a software development centre. He has practised software craftsmanship for 18 years (DDD, TDD, BDD) and now spends his time measuring what coding agents really do, rather than what we fear they do. He has proposed contributions to Google ADK Java, Spring AI A2A and AG-UI.
