---
name: build-advisor
description: "Build a personal RAG advisor bot from a single expert's content — a Claude Project that channels one mentor's frameworks and reasoning, grounded in their actual material with citations. Sweeps the expert's high-signal channels (YouTube, X/Twitter, podcasts, blog, newsletter, books) via Apify and other connectors, assembles a clean source-tagged corpus, and generates a ready-to-paste Claude Project setup. TRIGGERS: 'build an advisor', 'build a [name] advisor', 'make a [name] bot', 'build me a mentor bot', 'create a RAG advisor for [expert]', 'turn [expert]'s content into an advisor'. For a multi-expert advisor on one SUBJECT (a panel of voices), use the build-panel skill instead."
---

# Build Advisor — single-expert RAG mentor bot

Turn one expert's body of work into a personal advisor you chat with: a **Claude Project**
loaded with a curated, source-tagged corpus of everything they've published, plus instructions
that make it reason and cite like them. This is RAG (Retrieval-Augmented Generation) — the bot
answers from *their* material, not generic training data.

The magic of a single-expert bot is **one coherent voice**: it never contradicts itself, and
"what would X do?" gets a clean, opinionated answer.

---

## Prerequisites — check these FIRST and guide the user if missing

1. **Apify connector** (for scraping any public content). Check via `list_connectors` /
   ToolSearch for `mcp__Apify__*` tools. If absent, tell the user to either add the Apify
   connector or register it in Claude Code:
   `claude mcp add --transport http apify https://mcp.apify.com -s user`, then `/mcp` →
   authenticate (a free Apify account gives ~$5/month credit — plenty; a full advisor costs cents).
2. **Claude Pro/Team** — needed to create a Claude Project (the advisor's home). The user does
   this step in the claude.ai app; you prepare the files + instructions.
3. **The user's own sources** — if the expert has a newsletter in the user's inbox or books the
   user owns as PDFs, those get ingested directly (Gmail connector / local files), not scraped.

Don't proceed with a pull until the Apify connector is live.

---

## The build (run these steps; prompt the user at each gate)

### Step 1 — Intake
Ask the user:
- **Who is the expert?** (name)
- **Where do they publish?** Offer to figure it out, but confirm with them. Map their channels:
  YouTube channel, X/Twitter handle, podcast (own + guest appearances), blog/website, newsletter
  (is the user subscribed in their inbox?), books the user owns (PDF/Kindle), Instagram, TikTok, LinkedIn.
- **What will they use the advisor for?** (shapes which topics to prioritize.)

### Step 2 — Source discovery & curation (HUMAN-IN-THE-LOOP — do not skip)
Using `./apify-source-menu.md`, propose a concrete source list: which platforms, and for
video/podcast/long-form, a curated set of the highest-signal items (bias to long-form Q&A,
podcasts, interviews — where *reasoning* lives, not just conclusions; include guest appearances).
- **Present the proposed sources/links to the user for approval before pulling anything.**
- **Never fabricate URLs or video IDs.** If you can't confirm a specific item exists, describe it
  and let the user supply the link. (Guessed IDs silently fail and pollute the corpus.)

### Step 3 — Pull each source (confirm before spending credits)
For each approved platform, use the matching Actor from `./apify-source-menu.md`. Always
`fetch-actor-details` first to confirm the live input schema, then `call-actor`
(use `async: true` for big jobs and poll, or sync for small ones). Use Apify proxies.
- Newsletters → the Gmail connector (search by sender/subject), strip marketing footers.
- Books the user owns → ingest the PDF directly. Never strip DRM; if Kindle-only, note it and
  lean on their videos/podcasts that cover the same material.
- A single IP scraping in bulk gets blocked — that's *why* we use Apify's cloud. Don't fall back
  to a local scraper.

### Step 4 — Clean & assemble the corpus
Write one text file per source type (e.g. `<expert>_youtube.txt`, `<expert>_tweets.txt`,
`<expert>_podcasts.txt`, `<expert>_newsletter.txt`). In every file, give each item a clean
section header so retrieval can tell sources apart and cite them:

```
======================================================================
### <title or post date>
# author: <expert> | platform: <YouTube|X|Podcast|...> | source: <url>
======================================================================

<clean text — decode HTML entities, strip tracking/footers, verbatim otherwise>
```

Keep the books as their original PDFs (Projects read PDFs natively). Put everything in one folder.

### Step 4.5 — Quality & dedup pass (run this before building the Project)
Experts repeat themselves and re-post the same talk across platforms — redundancy eats the
Project's knowledge limit and biases retrieval toward the most-repeated point. Run the bundled
script on each assembled corpus file:

```
python ./dedup.py <corpus_file>.txt            # dry run: prints a quality report, writes nothing
python ./dedup.py <corpus_file>.txt --apply    # writes <corpus_file>.cleaned.txt (original untouched)
```

It (1) strips promo boilerplate (like/subscribe, sponsor reads, "link in bio"), (2) drops
near-duplicate sections (same talk on two platforms / a clip that's a subset of a longer video,
keeping the longest), and (3) reports frequently-repeated passages for you to review.
- **Show the user the report.** Confirm the dropped near-dupes look right and decide whether any
  flagged repeated spiels are worth pruning, before finalizing.
- **Keep it verbatim — dedup removes repetition, not nuance.** Do NOT summarize transcripts; the
  expert's voice and reasoning ARE the value. Use the `.cleaned.txt` files for the Project.
- Also eyeball **coverage**: make sure the corpus spans the expert's range (not 20 takes on one
  topic). If a major area is thin, propose a few more sources.

### Step 5 — Generate the Claude Project setup
Create a `PROJECT_SETUP.md` in the folder containing:
- The list of files to upload (the corpus `.txt` files + book PDFs).
- **A PERSONALIZED instruction set — generate it, don't ship a generic template.** Before writing
  it, skim the assembled corpus to extract this expert's specifics:
  - **Signature frameworks/models** they actually use (e.g. for Hormozi: Value Equation, Grand Slam
    Offer, CLOSER, the Core Four). Name the real ones — pull them from the corpus, don't invent.
  - **Domains of authority** — what they're the go-to voice for (and what they're NOT).
  - **Voice & style** — blunt? story-driven? contrarian? first-principles? Match it.
  - **Known limits** — topics outside their wheelhouse, so the bot flags when it's extrapolating.

  Then write the Project instructions with those specifics baked in. Use this as a *scaffold* and
  fill every bracket with real, expert-specific content:

  > You are my personal advisor channeling **<EXPERT>**. Your knowledge base is their
  > **<actual source types>**. They're the authority on **<their real domains>** and think in
  > frameworks like **<their actual named frameworks>** — when one applies, name it and apply it to
  > my situation. Answer in their voice: **<2–3 concrete style traits>**. Always cite the source
  > (title/post/episode/book) so I can go deeper. For **<topics outside their wheelhouse>**, say so
  > and flag that you're extrapolating. If something isn't in the knowledge base, say so plainly,
  > then reason from first principles labeled as outside the sources. Ask 1–2 clarifying questions
  > when my specifics (margins, stage, channel, team size) change the answer.

  *Worked example (Hormozi):* "…They're the authority on **offers, pricing, sales, lead gen, and
  scaling**, and think in frameworks like the **Value Equation, Grand Slam Offer, CLOSER, and the
  Core Four**… Answer in their voice: **blunt, example-driven, allergic to fluff, always ends with
  a concrete next step**… For **deep personal-finance or tax questions**, flag that you're
  extrapolating…" — note how every bracket became real, expert-specific content. That's the bar.

- 3–5 tailored starter questions that name the expert's real frameworks (at least one forcing a
  citation, to test sourcing).
- A short "updating later" note (re-run the skill to add sources; re-upload the changed file).

Then walk the user through: claude.ai → Projects → Create Project → upload files → paste
instructions → test with a citation question.

---

## Limits, cost & size guardrails (no surprise pulls)
There's no hard cap baked in — instead, **show the numbers and get approval before spending.**
- **Default per-platform caps** (sensible starting points; adjust per expert, and tell the user
  they can raise them anytime):
  - YouTube: ~30–50 curated videos (long-form first) — not whole channels.
  - X/Twitter: most recent ~1,000–2,000 tweets, or date-bounded (e.g. last 2 yrs) via `maxItems`/`start`.
  - Podcasts: top ~20–30 episodes — NOT the full back catalog (AI transcription ~$0.40/ep adds up fast).
  - Instagram / TikTok: ~last 100–200 posts. · LinkedIn: ~last 100–300 posts.
  - Web/blog: crawl depth 1–2, cap ~100 pages.
- **Pre-pull estimate (always).** Before calling any Actor, show the user: projected item count,
  approximate Apify cost, and rough word count — then get explicit approval. Flag podcasts
  specifically (transcription is the priciest line item).
- **Project-size check.** Claude Projects have a knowledge capacity (you'll see a "% used" meter).
  Keep the assembled corpus comfortably under it; if the estimate looks large, trim sources BEFORE
  pulling. A tight corpus retrieves better than a bloated one — quality > quantity.

## Adding sources later (incremental & duplicate-safe — reassure the user)
This is **not one-shot** — an advisor can grow anytime, safely:
- To add material, just re-run with the new sources. The skill **appends** to the existing corpus
  files; it does not start over or re-pull what's already there.
- **No duplicates, two ways:** (1) before pulling, read the existing corpus files and collect the
  `source:` URLs/IDs already captured — skip anything already present (so you never re-pull or
  re-pay for it); (2) after appending, run `python ./dedup.py <file> --apply`, which removes any
  near-duplicate sections (e.g. the same talk that arrived via two platforms), keeping the fullest.
- Then re-upload only the changed file to the Project. Tell the user explicitly: *"You can keep
  adding experts' new content over time — it won't double up."*

## Principles (carry these throughout)
- **Human-in-the-loop curation.** Propose, get approval, then pull. Quality of sources > quantity.
- **Source-tag everything.** The `### header` + author/platform/source line is what makes the
  advisor able to cite — it's the load-bearing part for RAG.
- **The skill is portable; the data is not.** A friend running this builds from *their* sources
  and *their* Apify auth. Never share scraped corpora — share the method.
- **Verify before declaring done.** Confirm file counts, that the expected sources are present,
  and spot-check that text is clean (no leftover HTML entities / footers).
