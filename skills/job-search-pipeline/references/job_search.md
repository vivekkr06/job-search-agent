# Stage 1: Job Search (SEARCH mode only)

**Job:** find relevant postings. Do not score, rank, or rewrite anything.

1. Read METADATA and SKILLS TAXONOMY from base_resume.md.
2. Use web search to find 5 to 8 active postings matching the preferences; prefer the last 30 days.
3. For each posting record: title, company, location (city plus remote/hybrid/onsite), date posted if available, source URL, a 3-sentence summary (what the company does, what the role owns, domain or stack), and a one-line instinct note citing something specific from base_resume.md.
4. Only return real postings with a source URL. If fewer than 5 real results exist, return what exists and say so. Never invent listings. Never apply or interact with a job platform for the user.
5. Save to `runs/_searches/YYYY-MM-DD_role-keyword.md`, one `## Job N: Title, Company` block per result.
