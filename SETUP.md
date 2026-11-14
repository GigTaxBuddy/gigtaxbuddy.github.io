# Gig Tax Buddy: how the automation works

Everything runs for free on GitHub. Nothing needs a computer to be on.

| Robot | When | What it does |
| --- | --- | --- |
| **Site check** | Every 30 minutes | Opens the website on a phone and a computer, tests the calculator, the app and the guides. If anything breaks, it opens an issue titled **"Website problem found"** (GitHub emails the owner) and closes it when fixed. |
| **Daily video, posts and report** | Every morning | Makes today's short video (script from `promo/scripts.json`, one per day until April 15), puts it on the site, posts it to every connected platform, then emails a **daily report**: sales, posts and website health. |

Both can also be run any time: **Actions** tab → pick the robot → **Run workflow**.

## Connecting accounts (one time each)

Secrets go in **Settings → Secrets and variables → Actions → New repository secret**. Platforms that are not connected are simply skipped.

| Secret | Where it comes from |
| --- | --- |
| `GUMROAD_TOKEN` | Gumroad → Settings → Advanced → Applications → create app → **Generate access token** |
| `META_TOKEN`, `IG_USER_ID`, `FB_PAGE_ID` | Meta for Developers app linked to the Gig Tax Buddy Facebook Page and Instagram professional account (long-lived Page token) |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | Google Cloud project with YouTube Data API v3, OAuth client, one-time consent by the channel owner |
| `TT_CLIENT_KEY`, `TT_CLIENT_SECRET`, `TT_REFRESH_TOKEN` | TikTok for Developers app with Content Posting API, one-time consent by the account owner (refresh token lasts a year) |

Notes from each platform's rules:
- YouTube and TikTok keep API uploads **private** until the platform reviews and approves the app. Instagram and Facebook post publicly.
- Profile links should use labels so the report shows where buyers come from: `https://gigtaxbuddy.github.io/?from=instagram`, `?from=tiktok`, `?from=youtube`.
- Every caption says the voiceover is AI-generated, and uploads set the platforms' AI-content flags.

## Changing content
- Video scripts: edit `promo/build_scripts.py`, run `python promo/build_scripts.py`.
- App screenshots used in videos: `promo/assets/`.
- Website: `index.html`. Guides: `guides/`.

Support email: gigtaxbuddy@gmail.com
