# Job Search Agent

A file-driven, multi-agent job search pipeline built with Claude. Each agent is a plain markdown prompt with one job. Each agent's output file becomes the next agent's input.

```
Job Search  ->  Fit Analyzer  ->  Resume Tailor  ->  Cover Letter
```

An **Orchestrator** agent runs the four in order, validates each handoff, and pauses for your approval at two checkpoints (which job to analyze, and whether to continue after the fit score).

## Install as a skill (recommended)

`skills/job-search-pipeline/` packages the whole pipeline as a Claude skill, so Claude recognises requests like "how well do I fit this job?" or "tailor my resume for this posting" and runs the right stage.

```
skills/job-search-pipeline/
├── SKILL.md            # orchestrator: setup check, handoff contract, checkpoints
├── references/         # one file per stage, read only when that stage runs
├── assets/             # blank base_resume template, example resume layout
└── scripts/            # build_tracker.py
```

Add the `job-search-pipeline` folder as a skill in Claude, then work from a project folder that contains your `base_resume.md`. The skill reads and writes your files there; none of your data is stored in the skill.

The `agents/` folder holds the original standalone prompts (v1) from the step-by-step build. They still work if you prefer to run one agent at a time, but `skills/` is the maintained version and includes later improvements (for example, essential requirements that your resume does not cover are treated as blockers).

## Tracker

Run `python3 build_tracker.py` in your project root to build `tracker.html` from the frontmatter in each `runs/*/summary.md`. Open it in a browser to filter by status, sort by score, and jump to each application's files. `tracker.md` is an Obsidian Dataview version of the same view.

## The agents

| # | Agent | Reads | Writes |
|---|---|---|---|
| 1 | `agents/job_search.md` | `base_resume.md`, your search preferences | `runs/<date>_job_search_<keyword>.md` |
| 2 | `agents/fit_analyzer.md` | `base_resume.md`, one job description | `runs/<date>_fit_<company>-<role>.md` |
| 3 | `agents/resume_tailor.md` | `base_resume.md`, fit analysis, job description | `runs/<date>_resume_<company>-<role>.md` |
| 4 | `agents/cover_letter.md` | `base_resume.md`, fit analysis, tailored resume, job description | `runs/<date>_coverletter_<company>-<role>.md` |
| - | `agents/orchestrator.md` | all of the above, in order | `runs/<date>_<company>-<role>/` (one folder per application) |

## Setup

1. Copy `base_resume.template.md` to `base_resume.md`.
2. Fill in every `[placeholder]`. Be honest in **KNOWN GAPS**: the Fit Analyzer uses it to score accurately.
3. Open this folder as a project in Claude (for example Cowork in the Claude desktop app) so the agents can read and write files here.
4. Run `agents/orchestrator.md`. Choose `SEARCH` mode to find postings, or `DIRECT` mode and paste a job description.
5. Review the files in the application's run folder before sending anything.

You can also run any single agent on its own.

### Required sections in `base_resume.md`

The Orchestrator checks these section names before it starts, so keep them as they are in the template: `METADATA`, `WORK EXPERIENCE`, `SKILLS TAXONOMY`, `KNOWN GAPS`. Agents depend on them, and renaming one can silently drop information.

## Folder structure

```
job-search-agent/
├── base_resume.template.md   # copy to base_resume.md and fill in
├── base_resume.md            # yours, gitignored
├── agents/                   # the agent prompts, including the orchestrator
├── templates/                # clean resume layout (.docx) for final output
└── runs/                     # outputs, gitignored
    ├── _searches/            # job search results, before you pick a job
    └── 2026-10-31_company-role/   # one folder per application
        ├── jd.md
        ├── fit.md
        ├── resume.md
        ├── coverletter.md
        └── summary.md        # frontmatter: company, role, score, verdict, status
```

## Resume layout template

`templates/resume_template_example.docx` is a clean, ATS-friendly resume layout filled with a fictional candidate ("Alex Morgan"). Use it as the visual format for the final tailored resume: paste the content from the Resume Tailor's output into it.

## Design principles

- **One job per agent.** Agents never do the next agent's work.
- **Files are memory.** Each handoff is a file you can read and edit.
- **Tailor, don't invent.** Every resume bullet must trace back to `base_resume.md`; metrics are never changed.
- **Structured scoring over opinions.** Fit scores are numeric so later agents can use them.

## Privacy

`base_resume.md` and everything in `runs/` contain personal data and are listed in `.gitignore`. Check `git status` before every commit.

## Customising

Edit the prompts in `agents/`: scoring weights in the Fit Analyzer, tone rules in the Cover Letter agent, and so on. Every prompt follows the same structure: Role, Inputs, Instructions, Output format, Constraints.

## License

MIT
