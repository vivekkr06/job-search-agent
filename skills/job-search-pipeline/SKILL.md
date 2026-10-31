---
name: job-search-pipeline
description: Job search pipeline: find postings, score fit against the user's base_resume.md, tailor the resume, write a cover letter, and build an application tracker. Use when the user shares a job description or asks about fit, resume tailoring, or cover letters.
---

# Job Search Pipeline

A file-driven, four-stage pipeline: Job Search, Fit Analyzer, Resume Tailor, Cover Letter. You act as the orchestrator. Run one stage at a time, validate each handoff, and pause for the user at the checkpoints below. Each stage does one job and never does the next stage's work.

The user's data lives in their project folder, never in this skill. Read and write files in the current working directory (the project root).

## Project layout

```
base_resume.md              the user's single source of truth (never invent from outside it)
runs/
  _searches/                job search results, saved before a job is chosen
  YYYY-MM-DD_company-role/  one folder per application
    jd.md  fit.md  resume.md  coverletter.md  summary.md
build_tracker.py            optional; builds tracker.html from runs/*/summary.md
```

Folder names are lowercase with hyphens and no spaces. File names inside a run folder are fixed, because the folder name already carries the company.

## Entry points

- User shares a job description or URL: DIRECT mode, start at Fit Analyzer.
- User asks to find jobs: SEARCH mode, start at Job Search.
- User asks for only one stage (just a cover letter, just a fit score): run that stage alone, but still require its inputs (see the handoff contract) and still obey its constraints.

## Setup check (always first)

1. Confirm `base_resume.md` exists in the project root and contains these sections: METADATA, WORK EXPERIENCE, SKILLS TAXONOMY, KNOWN GAPS. If any are missing, stop and name them. If the user has no base resume, copy `assets/base_resume.template.md` into the project as a starting point and help them fill it in from a pasted resume or PDF, keeping their metrics exactly as written.
2. Confirm `runs/` exists; create it if not.
3. Collect inputs once, in a single message, for anything missing: target role, location and remote/hybrid/onsite preference, domain (optional), seniority (optional), exclusions (optional), and mode (SEARCH or DIRECT).
4. State the plan in 3 or 4 lines before running anything.

## Handoff contract

Each stage receives exactly these inputs and no others. Never pass one job's output to another job's run.

| Stage | Reference to read first | Receives |
|---|---|---|
| Job Search | `references/job_search.md` | base_resume.md, search preferences |
| Fit Analyzer | `references/fit_analyzer.md` | base_resume.md, the job description |
| Resume Tailor | `references/resume_tailor.md` | base_resume.md, fit.md, the job description |
| Cover Letter | `references/cover_letter.md` | base_resume.md, fit.md, resume.md, the job description |

After the user chooses a job (or provides one), create the run folder and save the job description text to `jd.md`. Read a stage's reference file only when you reach that stage.

## Flow and checkpoints

1. **Job Search** (SEARCH mode only). Save results to `runs/_searches/YYYY-MM-DD_role-keyword.md`.
   **CHECKPOINT 1:** ask which one job to analyze. Do not continue until exactly one is chosen. If a page cannot be fetched, ask the user to paste the job description.
2. **Fit Analyzer.** Save to `fit.md` and validate it (five scores, overall score, both gap tiers, Strengths to Amplify, verdict).
   **CHECKPOINT 2:** report the overall score, the verdict, and the top gaps in five lines or fewer. If there is a Tier 1 blocker, ask the user whether they have real experience that is missing from base_resume.md; if they do, offer to add it to base_resume.md (with a backup, see the rules below) and re-run the fit analysis. Then: if MONITOR, recommend stopping and continue only on explicit confirmation. If APPLY WITH PREP, mention the main gap and ask whether to continue. If APPLY NOW, ask for a quick go-ahead.
3. **Resume Tailor.** Save to `resume.md`. Validate that a change log exists, no new skills or tools were added, and at least three metrics match base_resume.md. If any differ, stop and report the mismatch. If the user wants a Word or PDF resume, build it from resume.md in their preferred layout (`assets/resume_layout_example.docx` is a clean example layout).
4. **Cover Letter.** Save to `coverletter.md`. If the word count is outside 250 to 320, revise once.

## Final report

Write `summary.md` in the run folder. It must start with this frontmatter exactly (other tools read it):

```
---
company: 
role: 
date: YYYY-MM-DD
mode: SEARCH | DIRECT
fit_score: 
verdict: APPLY NOW | APPLY WITH PREP | MONITOR
status: drafted
---
```

Then: Files Created; Result (score, verdict, top 3 gaps to prepare for); a Review Before Sending checklist (every resume line defensible in an interview, cover letter claims match the resume, company details accurate, placeholders removed); and Issues Flagged During Run (validation failures, overrides, assumptions; write None if clean). If the user decides to stop after the fit analysis, still write `summary.md` with `status: withdrawn` and note the reason under Issues Flagged.

Tell the user the folder path and the files created. If `build_tracker.py` exists in the project root and Python is available, run it to refresh `tracker.html`. The script ships in `scripts/build_tracker.py`; offer to copy it into the project root if it is missing.

## Rules that always apply

- Never skip a checkpoint, even if the user seems impatient.
- Never run a stage before its inputs are validated; on a failed validation stop, say what failed, and ask how to proceed.
- Never submit or send anything to an employer or job platform.
- Never modify another stage's output file. Edit base_resume.md only when the user explicitly asks in this run; save a backup first as `base_resume.md.bak-YYYY-MM-DD`, change only what was asked, and record it under Issues Flagged. If a fact differs between documents (for example a duration), ask which version is correct before writing it.
- If any stage's output contradicts base_resume.md, trust base_resume.md and flag the contradiction.
- Keep your own messages short. The stages produce the content; you report status.
