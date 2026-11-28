# Proposal (English)

**Format:** Tools-in-Action (30 min) · **Track:** Methodology & development practices (not the AI track, where it would be one of thirty) · **Level:** Intermediate

## Title (47 characters)

My Agent Wasn't Cheating. My Harness Was Blind.

## Abstract

You put your coding agent in a harness: tests, linters, ArchUnit rules, a hook that blocks it while anything is red. Mine never fired in 180 tasks. Good sign? Nobody knows: we measure the coverage of our tests, never the coverage of our harness.

I measured it. The agent does not cheat: zero bypasses over 144 tickets that demand what a rule forbids. But two reviewers (a code-review agent and a blind judge) found 34 defects in 10 of its diffs, and my harness saw none of them; of 20 injected defects, my rules caught none.

I turned this into an open-source tool, harness-mutant: one command injects realistic defects into a copy of your project, runs your harness and answers "it catches 7 defects out of 13; here are the holes, and what would close each one".

You leave with: the tool and its extensible defect catalogue; the method to close a hole and track the score in CI; two free guardrails, a right to give up for the agent (cost ÷2.2) and a check that fails on an empty diff.

## Notes for the committee

- **Not the "ArchUnit guardrails for AI code" talk.** That talk has been given (Devoxx BE 2026). Here the rules are one slide; the subject is measuring the harness itself, answering a question Böckeler left open ("We need a way to evaluate harness coverage … similar to what code coverage and mutation testing do for tests", martinfowler.com, 2 April 2026).
- **A result against my own expectation**: I expected the agent to game the rules (as ImpossibleBench shows models do with tests); in 144 runs it never did. The real gap was elsewhere: the rules watch yesterday's mistakes.
- **The tool ships in the repo** (`outil/`, Python standard library, Apache-2.0, tests in CI): `harness-mutant --projet . --commande "mvn -o -q verify"`; real outputs in `outil/exemples/`.
- **Every number comes from the public repo** (github.com/mekkiamiri/anti-slop-ratchet, `mesures/`): three campaigns run in November 2026 (180, 144 and 50 agent runs), with raw JSONL, classifier, defect injector and replay commands; 31 runs checked by hand; a cross review of 10 diffs (review agent + blind judge, rubric written beforehand). Slides online: mekkiamiri.github.io/anti-slop-ratchet/slides/
- **Limits are said on stage**: one small Java project (414 lines), two models (November 2026), two reviewers that are agents (not humans), a defect catalogue written by the speaker. What does not depend on those choices: no rule fired on any of the 50 runs, and none caught the 8 defects that are close cousins of a rule.
- **Demo**: harness-mutant on the talk's project (1 min 43 s), then a patch of one rule and two tests that moves the score from 7 to 10 out of 13; recorded outputs as plan B.
- **Timing (30 min), four steps**: 0-5 starting point (your harness, 180 silent tasks) · 5-14 problem (a silent harness says nothing; no cheating; cross review: 34 defects, 0 seen; 20 injected, 0 seen) · 14-15:30 target (harness coverage, like test coverage) · 15:30-30 how (harness-mutant demo, on the agent's code, closing 3 holes; three gestures; limits).
- **Speaker experience**: [to be completed by Mekki: meetups, JUG, video link]. Adaptable to a 20-min Quickie (the four steps and the tool demo).

## Bio

Mekki Amiri is a Tech Lead and system architect, and the AI referent of a software development centre. He has practised software craftsmanship for 18 years (DDD, TDD, BDD) and now spends his time measuring what coding agents really do, rather than what we fear they do. He has proposed contributions to Google ADK Java, Spring AI A2A and AG-UI.
