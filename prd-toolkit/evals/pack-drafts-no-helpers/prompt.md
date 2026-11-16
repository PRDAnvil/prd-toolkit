---
max_turns: 100
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

You showed me the proposal below in your last message, in this same conversation: a pack from
north/docs/prd/north and south/docs/prd/south. I am the owner, and this message is my reply to it, item by item,
given after reading it. Your proposal:

> **The pack:** `leaflet`, `version: 0.1.0`, `toolkit: >=0.8.0,<0.9` (the built-in packs' range), description
> "Small static leaflet sites, written from the north and south PRDs."
>
> **Contract types.** `pages` (both; north/prd.md and south/prd.md section 7 row `pages`): files
> `contracts/pages.yaml`, validator `python3 contracts/check_pages.py`, the same file in both (`cmp` exit 0),
> carried over as `${PACK}/check_pages.py`; recommended in. `routes` (both; section 7 row `routes`): files
> `contracts/routes.yaml`, its `python3 -c` validator as it stands; recommended in. `forms` (A, north only) and
> `feeds` (B, south only) cannot go in: the check runs each type on both PRDs. Target kinds `pages` and `routes` go
> in with their types.
>
> **Levels.** `unit` (both; testing.md Levels row `unit`, `python3 -m pytest tests/unit`, local, build):
> recommended in. `integration` differs: A `python3 -m pytest tests/integration`, B `python3 -m pytest tests/site`;
> recommended out, so each PRD keeps its own.
>
> **Harness.** Every slot marked both (Lifecycle, Environment switch, Database access, Clean state, Persistent
> environments, Layout, HTTP requests, Fixtures, Browser identity, Assertions, Waits, Effects, Leaks, Acceptance):
> recommended in. `Tools on the runner` differs: A "python3 on PATH; ...", B "python3 and a headless browser on
> PATH; ..."; recommended out.
>
> **Standards** `site/**/*.html` with `python3 tools/check_html.py` (both): in. **Skills** "a change to a page",
> `code-review` (both): in. **Vocabulary:** every candidate recommended out.
>
> **What will be written:** `pack.yaml`; `check_pages.py`, copied unchanged; `samples/pages/bad.yaml` (north's
> `contracts/pages.yaml` with its `path:` line cut) and `samples/routes/bad.yaml` (north's `contracts/routes.yaml`
> cut to its first line); and `README.md` with the to-do list (the harness helpers each site's tests use, the
> clarify questions for this kind, and the rules a skill for it would need, each naming the files to start from).
>
> **Where it goes:** which plugin checkout should hold it?

My reply, item by item: name it `leaflet`, with your description. `pages` and `routes` in, with their
validators and target kinds; `forms` and `feeds` out. Levels: `unit` in, `integration` out. Harness: every
slot marked both in, `Tools on the runner` out. The standards row in, the skills row in, no vocabulary word.
The samples as you proposed. Write it into the plugin checkout at plug/ (in this folder) and commit it there.

That decides every item and names the plugin. Steps 1 to 3 are done, so go on from step 4, with step 5's plugin
checks, then step 6. I'm offline after this message, so don't ask me anything.
