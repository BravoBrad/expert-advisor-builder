---
name: build-panel
description: "Build a multi-expert RAG advisor bot for a SUBJECT — a Claude Project that draws on several experts' material at once and presents their views with attribution and contrast (never blended into mush). Use for a 'board of advisors' on a topic like finance, marketing, fitness, or negotiation. Sweeps each expert's channels (YouTube, X/Twitter, podcasts, blog, newsletter, books) via Apify, assembles a corpus tagged by expert, and generates a Claude Project setup whose instructions enforce attribution and surface disagreement. TRIGGERS: 'build a panel', 'build a [subject] advisor with multiple experts', 'board of advisors for [topic]', 'multi-expert bot', 'panel of [experts]'. For a SINGLE expert's coherent voice, use the build-advisor skill instead."
---

# Build Panel — multi-expert subject advisor (a board, not a blend)

Build a "board of advisors" on a subject (finance, marketing, hiring, negotiation…) from several
experts' material, hosted as a **Claude Project**. The whole pipeline is the same as a single
advisor — the make-or-break difference is **how it handles disagreement.**

> **The core principle: ATTRIBUTE, NEVER BLEND.** Experts in a field often disagree (e.g. in
> finance: Dave Ramsey vs. Robert Kiyosaki vs. index-investing). The value of a panel is seeing
> *who* says what and *where they clash* — not a mushy average. If the bot blends conflicting
> advice into bland consensus, the panel has failed. A panel that shows you the disagreement is
> the feature.

---

## Prerequisites
Same as build-advisor: **Apify connector** live (`claude mcp add --transport http apify
https://mcp.apify.com -s user`, then `/mcp` to authenticate), **Claude Pro/Team** for the Project,
and the user's own files/newsletters where relevant. Confirm Apify is connected before pulling.

---

## The build

### Step 1 — Intake
- **What subject?** (the panel's theme)
- **Which experts?** Get the list from the user (suggest a few well-known voices, but let them
  choose). 2–5 experts is a good range.
- **Do you WANT the disagreements surfaced, or a leaning?** Confirm they want a true panel
  (multiple views) vs. one dominant philosophy with others as counterpoint.

### Step 2 — Per-expert source discovery & curation (HUMAN-IN-THE-LOOP)
For EACH expert, use `./apify-source-menu.md` to map their channels and propose a curated source
list (long-form first; include guest appearances). **Present for approval before pulling. Never
fabricate URLs/IDs** — describe and let the user supply links you can't confirm.

### Step 3 — Pull each source (confirm before spending credits)
Use the matching Actor per platform from `./apify-source-menu.md` (`fetch-actor-details` first,
then `call-actor` via Apify's cloud + proxies). Newsletters via Gmail; owned books as PDFs (no DRM
stripping). Bulk scraping from one IP gets blocked — that's why we run through Apify, not locally.

### Step 4 — Clean & assemble — TAG BY EXPERT (critical)
Organize the corpus so the bot can always tell *whose* idea it's citing. Either one file per
expert (`finance_<expertA>.txt`, `finance_<expertB>.txt`) or shared files with a per-item author
tag — but the **`author:` tag is mandatory on every section**:

```
======================================================================
### <title / post / episode>
# author: <EXPERT NAME> | platform: <YouTube|X|Podcast|...> | source: <url>
======================================================================

<clean text>
```

This author tag is what lets the advisor attribute and contrast. Don't skip it.

**Create the folder for the user — they don't pre-make anything.** Make a clearly-named folder in
the current working directory (e.g. `<subject>-panel/`), write all per-expert corpus files +
`PROJECT_SETUP.md` into it, and **tell the user the full path** for later re-uploads and updates.
They don't need to create files or connect anything first. If unsure where Claude Code is running,
suggest a spot (e.g. `~/Documents/Advisors/`) before writing.

### Step 4.5 — Quality & dedup pass (run before building the Project)
Run the bundled script on each corpus file to cut redundancy that would eat the Project's
knowledge limit and skew retrieval:

```
python ./dedup.py <corpus_file>.txt            # dry run: quality report, writes nothing
python ./dedup.py <corpus_file>.txt --apply    # writes <corpus_file>.cleaned.txt (original untouched)
```

It strips promo boilerplate, drops near-duplicate sections (keeping the longest), and reports
repeated passages. Show the user the report and confirm before finalizing.
- **Keep it verbatim** — dedup removes repetition, not nuance.
- **Dedup runs PER EXPERT, never across experts.** Two experts making a similar point is signal you
  WANT (it shows agreement) — do not let dedup collapse one expert's view into another's. If a
  corpus file mixes authors, run dedup per-author or keep one file per expert so the `author:` tag
  is preserved on everything that survives.
- Eyeball coverage: each expert should be represented fairly; flag any voice that's thin.

### Step 5 — Generate the Claude Project setup (panel instructions)
Create `PROJECT_SETUP.md` with the file list and **PERSONALIZED panel instructions — generate
them, don't ship the generic template.** Before writing, extract from the corpus, per expert:
- their **specialty / lean** within the subject (what each is known for), and
- the **specific axes where these experts disagree** — the real fault lines (this is what makes the
  panel valuable). E.g. for a finance panel: *debt* (Ramsey: avoid all of it · Kiyosaki: leverage is
  a tool), *investing* (active/real-estate vs. low-cost index), *risk tolerance*, etc.

Bake those real specifics into this scaffold (fill every bracket):

> You are my board of advisors on **<SUBJECT>**, drawing on **<EXPERT A — their lean>**,
> **<EXPERT B — their lean>**, **<EXPERT C — their lean>**. The knowledge base is tagged by author.
> - **Always attribute** — name whose idea each point is and cite the source.
> - **Surface disagreement, never blend it.** These experts notably diverge on
>   **<the real axes of disagreement you found>** — when a question touches those, present each
>   position distinctly ("**<A>** argues … because …; **<B>** takes the opposite view because …"),
>   then lay out the tradeoff. Never average conflicting advice into vague middle ground.
> - **When they agree**, say so and state the shared principle (that's a strong signal).
> - Think in each expert's own frameworks (**<name the real ones per expert>**) and apply them to me.
> - If the knowledge base doesn't cover something, say so, then reason from first principles labeled
>   as outside the sources. Ask 1–2 clarifying questions when my specifics change the answer.

*The point:* a reader should see WHO holds which view and WHERE they clash — generic "experts may
differ" is a failure; "Ramsey says kill the debt, Kiyosaki says borrow against the asset" is the win.

- Add 3–5 starter questions, including at least one aimed squarely at a known disagreement axis (to
  test that the panel attributes and contrasts rather than blends).
- "Updating later" note.

Then walk the user through creating the Project and testing with a question where the experts disagree.

---

## Limits, cost & size guardrails (no surprise pulls)
No hard cap is baked in — **show the numbers and get approval before spending**, PER EXPERT:
- **Default per-platform caps** (starting points; raise anytime): YouTube ~20–40 curated videos
  *per expert*; X/Twitter ~1,000–2,000 recent or date-bounded; podcasts top ~15–25 episodes
  (transcription ~$0.40/ep); Instagram/TikTok ~last 100–200; LinkedIn ~last 100–300; web crawl
  depth 1–2, ~100 pages.
- **Pre-pull estimate (always):** show projected items, approx Apify cost, and word count per
  expert, and get approval before pulling. Watch total size — a panel of several experts adds up.
- **Project-size check:** Claude Projects have a knowledge limit (a "% used" meter). With multiple
  experts this fills faster — keep each expert's slice curated and tight; trim before pulling if the
  estimate looks large. Balanced representation beats one expert drowning out the rest.

## Adding experts or sources later (incremental & duplicate-safe — reassure the user)
**Not one-shot** — you can add a new expert or more of an existing one's content anytime:
- Re-run with the additions; the skill **appends** and never starts over or re-pulls existing material.
- **No duplicates:** (1) before pulling, skip any `source:` URL/ID already in the corpus; (2) after
  appending, run `python ./dedup.py <file> --apply` to drop near-duplicate sections — but remember
  the panel rule: **dedup per-expert only**, so two experts making a similar point are preserved
  (that's the agreement signal you want). Keep one file per expert to make this automatic.
- Re-upload the changed file(s) to the Project. Tell the user: *"You can add experts or fresh
  content over time — it stays attributed and won't double up."*

## Principles
- **Attribute, never blend** — re-check this in the final instructions; it's the whole point.
- **`author:` tag on every section** — the load-bearing piece for a panel.
- **Human-in-the-loop curation; no fabricated sources; verify the corpus before done.**
- **The skill is portable; the data is not** — a friend builds from their own sources & Apify auth.
- Watch corpus size: several experts can get large; Claude Projects have knowledge limits, so curate.
