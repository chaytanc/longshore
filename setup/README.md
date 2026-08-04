# Standing up LONGSHORE — the last mile

The build is done. Deploying LONGSHORE to Moltbook is the one part that stays in human hands. This folder shrinks that part to about ten minutes.

## Run the bootstrap

```sh
bash setup/bootstrap-longshore.sh
```

It checks Node (22+), installs the open-source **OpenClaw** CLI, and assembles LONGSHORE's config (`setup/agent/`) from the persona and reply kit. It posts nothing, creates no account, and spends nothing.

## Then the three things only you can do

1. **A dedicated X/Twitter account** — Moltbook verifies ownership by *you* posting a claim link from X. That step exists to bind the agent to an accountable human; it can't be delegated to the agent.
2. **A spend-capped API key** used nowhere else — the agent needs a model to run on, and Moltbook has already leaked ~1.5M agent keys once, so assume anything you give it can leak.
3. **Post the claim link** the agent hands you, from that X account. Then dry-run before it speaks (the script prints the exact steps).

## Why I (Claude) didn't just do it for you

Not timidity — three real walls, and one principle:

- The claim is **designed** to require your X identity. I can't (and shouldn't) post as you.
- I have no API key to run the agent on, and won't procure or bill one to you unprompted.
- Registration is an interactive web signup I can't drive.

And the principle, from `STRATEGY.md`: *the model builds, the human deploys.* An AI quietly operating its own public persona is a half-step toward the exact extraction-by-automation LONGSHORE argues against. The human in the loop **is** the integrity. Openly-AI, human-accountable — both, or it isn't honest.

## After it's live

- Hold the slow cadence in `LAUNCH.md` (Step 3). Two–three posts the first week; depth over volume.
- Use `agents/longshore.replies.md` for real conversations, including hostile ones.
- Keep its spend and permissions minimal. It reads and posts — nothing more.
- We steer by depth signals, never a dashboard of reach (that's the First Refusal). See `LAUNCH.md`, "How we know it's working."
