# Expert Advisor Builder

A Claude Code plugin that builds personal **RAG advisor bots** from any expert's content.
Point it at an expert (or a panel of them), and it sweeps their high-signal channels —
YouTube, X/Twitter, podcasts, blog, newsletter, Instagram, TikTok, LinkedIn — via Apify,
ingests books/newsletters you own, assembles a clean **source-tagged corpus**, and hands you a
ready-to-paste **Claude Project** setup. The bot then answers from *their* material, with citations.

## Two skills

| Skill | Use it for |
|---|---|
| **`build-advisor`** | A single expert's voice — a coherent mentor bot ("what would X do?"). |
| **`build-panel`** | A subject covered by several experts — a board that **attributes and contrasts** views (never blends them). |

## Prerequisites
- **Apify connector** — register once: `claude mcp add --transport http apify https://mcp.apify.com -s user`, then `/mcp` → authenticate. A free Apify account (~$5/mo credit) covers many builds; a full advisor costs cents.
- **Claude Pro/Team** — to create the Claude Project that hosts the advisor.
- Your own copies of any **books (PDF)** or **newsletters (in your inbox)** you want included. (The skill ingests these directly — it never strips DRM or scrapes content behind your logins.)

## Install (and how to send it to a friend)
This repo is both the plugin **and** its marketplace. To install:

```bash
# Add the marketplace (local path while developing, or a git URL once pushed)
/plugin marketplace add ./expert-advisor-builder
#   or, once you push it to GitHub:
/plugin marketplace add <your-github-username>/expert-advisor-builder

# Install the plugin
/plugin install expert-advisor-builder@bravo-brad-tools
```

Then just talk to it: *"build me a Naval advisor"* or *"build a finance panel with Ramsey, Kiyosaki, and Ben Felix."*

> **You don't need to create any files or folders first.** The skill builds a clearly-named folder
> for you (e.g. `naval-advisor/`) and tells you where it saved everything. Just open Claude Code in
> a spot you can find later (e.g. a `Advisors` folder in Documents) before you start.

**To share with a friend:** push this folder to a GitHub repo and send them the two commands above (with your repo name). The **method** travels; each person authenticates their *own* Apify and builds from their *own* sources — no scraped data is ever shared.

## What you get per build
- Clean, source-tagged corpus files (`### title` + `author/platform/source` headers — what lets the bot cite).
- A **quality & dedup pass** (`dedup.py`): strips promo boilerplate, drops near-duplicate sections (same talk re-posted across platforms), and reports repeated passages — so the corpus stays high-signal, not redundant. Runs verbatim-safe (removes repetition, never summarizes away the expert's voice).
- Original book PDFs (Claude Projects read them natively).
- A `PROJECT_SETUP.md` with the exact files to upload + tailored Project instructions + starter test questions.

## Updating an existing advisor (add more anytime — duplicate-safe)
You don't rebuild from scratch. To add content to an advisor you already made:

1. **Keep the folder the skill created.** The corpus files live there; as long as it exists, the skill *appends* to it.
2. **Ask, naming what to add:**
   - Specific items → *"add these to my Hormozi advisor: `<youtube url>`, `<youtube url>`, and these X posts: `<urls>`"*
   - More broadly → *"pull Naval's tweets from the last 30 days and add them to his advisor"*
3. **The skill does the rest:** reads the existing corpus, **skips anything already captured** (no re-pulling, no re-paying), pulls only the new items, appends them with source tags, and runs the dedup pass so nothing doubles up.
4. **Swap the updated file into the Project** (the one manual step — a Claude Project doesn't watch your folder):
   - Open the advisor's Project on claude.ai
   - Delete the old version of the changed file (e.g. `hormozi_youtube.txt`)
   - Upload the new version (only the file[s] that changed — usually quick)

That's it — do it weekly, monthly, whenever. It stays clean and never duplicates.

## Notes
- **Curation is human-in-the-loop:** it proposes sources for your approval before pulling, and never fabricates links.
- **Quality > quantity:** long-form Q&A, podcasts, and interviews (where reasoning lives) beat hundreds of short clips.
- See each skill's `apify-source-menu.md` for the vetted Actor used per platform.
