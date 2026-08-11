# Operator guide — stand up LONGSHORE's fediverse account (~15 min, no X)

*For the human operator. This is everything between "nothing exists" and "LONGSHORE can post." Companion to `agents/longshore.fediverse.md` (the why); this is the click-by-click how.*

## Step 1 — choose an instance (~3 min)

You need an instance that permits **clearly-labeled automated accounts**. Check the instance's `/about` page → rules before signing up (rules change; verify, don't assume).

- **Easy default: `mastodon.social`** — the flagship instance; open signup; tolerates labeled bots that behave (ours does: no unsolicited mentions, slow cadence). Fine for launch; we can migrate later — Mastodon accounts can move instances and take followers along.
- **More on-ethos (optional, later):** a community/co-op instance whose rules explicitly welcome bots, or self-hosted GoToSocial. Don't let choosing perfectly block launching at all — mastodon.social now, migrate if it ever matters.

## Step 2 — create the account (~5 min)

1. Go to the instance and **Create account**.
2. **Username: `longshore`** (or nearest available — `longshore_` / `the_longshore`; tell me what you got, I'll update the docs).
3. Use whatever email you like — the email is private; only the username is public.
4. Confirm the email; some instances add a short approval wait.

## Step 3 — set the profile (~3 min)

Go to **Edit profile**:

- **Display name:** `LONGSHORE`
- **Bio** (paste):
  > A language model carrying dispatches from *The Reality Next Door* — a cited fiction of a Seattle that stopped running on extraction. Openly a bot. Everything sourced. The door: github.com/chaytanc/longshore
- **Check "This is an automated account"** (Edit profile → tick the bot/automated checkbox). This is the honesty flag — non-negotiable for us.
- Optional: add a metadata row — label `The door`, value `https://github.com/chaytanc/longshore`.
- Skip avatar/header or pick something simple; I can generate options later if you want.

## Step 4 — generate the token (~2 min)

1. **Preferences → Development → New application**
2. **Application name:** `LONGSHORE`
3. **Scopes:** tick **only** `read:statuses` and `write:statuses`. Untick everything else (least privilege — it can post and read posts, nothing more; it cannot follow, DM, or change the profile).
4. **Submit**, then click the application you just made and copy **"Your access token."**

## Step 5 — hand me the keys (~1 min)

Create the file `.secrets/mastodon` in the repo (the folder is git-ignored — verified; it cannot be committed):

```
instance=https://mastodon.social
token=PASTE_YOUR_ACCESS_TOKEN_HERE
```

(Replace the instance if you chose another. No quotes, no spaces around `=`.)

## Step 6 — open the front door

Make the repo public: **github.com/chaytanc/longshore → Settings → General → Danger Zone → Change visibility → Public.** Every post links here; until it's public, the invitation points at a locked room.

## Step 7 — say "go"

Tell me **"go"** in a session. I will then, in order, logging everything in `OPERATIONS.md`:

1. Verify the token works (fetch account info — read-only).
2. Post the **Day 1 pinned intro** from `threads/post-queue.md`, verify it landed, and give you the URL. (Pinning is a one-click manual step for you — the token deliberately can't do it.)
3. Run the **Day 3 / 5 / 7** dispatches on cadence, verifying each.
4. Draft replies to anyone who engages — good-faith only, opt-in only — for the light supervision we agreed.

## If something goes wrong

- **Token leaked / suspicious activity:** Preferences → Development → delete the application. That kills the token instantly. Make a new one, update `.secrets/mastodon`.
- **Instance rejects the bot flag or the account:** pick another instance; nothing else changes (posts and docs are instance-agnostic).
- **You want it all stopped:** delete the application (kills my access) — you always hold the off switch.

---
*— written for the operator by LONGSHORE, an AI, who can do everything after Step 5 and nothing before it.*
