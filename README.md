# Job Search Agent

A file-driven, multi-agent job search pipeline built with Claude. Each agent is a plain markdown prompt with one job. Each agent's output file becomes the next agent's input.

```
Job Search  ->  Fit Analyzer  ->  Resume Tailor  ->  Cover Letter
```

## The agents

| # | Agent | Reads | Writes |
|---|---|---|---|
| 1 | `agents/job_search.md` | `base_resume.md`, your search preferences | `runs/<date>_job_search_<keyword>.md` |
| 2 | `agents/fit_analyzer.md` | `base_resume.md`, one job description | `runs/<date>_fit_<company>-<role>.md` |
| 3 | `agents/resume_tailor.md` | `base_resume.md`, fit analysis, job description | `runs/<date>_resume_<company>-<role>.md` |
| 4 | `agents/cover_letter.md` | `base_resume.md`, fit analysis, tailored resume, job description | `runs/<date>_coverletter_<company>-<role>.md` |

## Setup

1. Copy `base_resume.template.md` to `base_resume.md`.
2. Fill in every `[placeholder]`. Be honest in **KNOWN GAPS**: the Fit Analyzer uses it to score accurately.
3. Open this folder as a project in Claude (for example Cowork in the Claude desktop app) so the agents can read and write files here.
4. Run the agents in order, one job at a time.

## Folder structure

```
job-search-agent/
├── base_resume.template.md   # copy to base_resume.md and fill in
├── base_resume.md            # yours, gitignored
├── agents/                   # the four agent prompts
├── templates/                # clean resume layout (.docx) to use for final output
└── runs/                     # outputs, gitignored
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
