# Apify Source Menu — proven Actors per platform

Use this to pull an expert's content from wherever they publish. All Actors below are
non-deprecated, high-trust, and take simple handle/URL inputs. Call them via the Apify
MCP (`call-actor`) — always `fetch-actor-details` first to confirm the live input schema,
since schemas can change. Prefer Apify proxies (`proxyOptions: {useApifyProxy: true}`).

| Platform | Actor (`username/name`) | Key input | Pricing (approx) | Caveat |
|---|---|---|---|---|
| **YouTube transcripts** | `karamelo/youtube-transcripts` | `urls` (array of video/channel URLs); `outputFormat: "singleStringText"`; `maxRetries: 8` | ~$0.005–0.007 / transcript | Returns `title`, `channelName`, `captions` (transcript). Captions are raw auto-caption text (no punctuation) — fine for RAG. Alt: `starvibe/youtube-video-transcript`. |
| **X / Twitter** | `danek/twitter-scraper-ppr` | `username` (ONE handle per run, no @), `search_type: "Latest"`, `max_posts` | ~$0.24 / 1K posts | **Reliable on the free tier** (free tier caps ~20 posts/run). Run it once per person. ⚠️ `apidojo/tweet-scraper` looks higher-volume but returned empty (`noResults`) on free credit with both `twitterHandles` and `startUrls` — it needs a paid proxy tier, so only use it if you have one. Filter out retweets (`text` starting with "RT @") when building the corpus. |
| **Podcasts (transcripts)** | `agentx/video-transcript` | episode audio/video URL | ~$0.40 / episode (incl. AI speech-to-text) | Two-step: first get episode/audio URLs from the show's RSS or an Apple/iTunes scraper, then transcribe each here. No single "name → transcripts" actor exists. |
| **Instagram** | `apify/instagram-post-scraper` | `username` (array of handles) | ~$0.0017 / post | Official. Returns captions + metrics. No login. |
| **TikTok** | `clockworks/tiktok-profile-scraper` | `profiles` (handles/URLs) | ~$0.004 / result; transcript add-on ~$0.05/min | Captions free; spoken-word transcripts cost extra. For transcript-heavy use, `agentx/video-transcript` also handles TikTok. |
| **LinkedIn** | `harvestapi/linkedin-profile-posts` | `profiles` / profile URLs | ~$0.002 / post | Prefer this — no cookies/login (avoids account-ban risk of cookie-based actors). |
| **Web / blog / articles** | `apify/website-content-crawler` | `startUrls` (array); crawl depth/glob controls | Free (pay compute only) | Official, built for RAG clean-text. For a few known article URLs or a search query, use `apify/rag-web-browser` instead. |

## How to choose per expert
Ask where the expert actually publishes and weight by where their *reasoning* lives:
- **Long-form first** (podcasts, long YouTube, interviews) — that's where the thinking is, not just conclusions.
- **X/Twitter** for aphorism-heavy thinkers (e.g. Naval).
- **Blog/newsletter** for writers; ingest **books** the user owns as PDFs directly (no scraping).
- **Guest appearances** matter — search the expert's name on YouTube/podcasts, not just their own channel.

## Non-Apify sources (use the right tool)
- **Newsletters in the user's own inbox** → the Gmail connector (search by sender/subject), not Apify.
- **Books / PDFs the user owns** → ingest the files directly. Never strip DRM; if a book is Kindle-only, note it and rely on the expert's videos/podcasts that cover the same material.
- **Anything behind a login the user owns** → ask the user to export it; don't scrape authenticated content.
