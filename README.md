# TicketDesk (Python)

> ⚠️ **Deliberately vulnerable code.** TicketDesk is a realistic-looking but intentionally insecure application, built for security training. Never deploy it, expose it to a network, or reuse its code. The compose file and dev server bind the API to `127.0.0.1`.

A multi-tenant **customer support ticketing API**, written the way many real SaaS backends are: FastAPI routers, a service layer, SQLAlchemy repositories, background workers, server-rendered portal pages and admin tooling. About 60 Python files.

It's the **realistic target** in the vuln-scan workshop. Its bugs are hidden the way real ones are: two or three calls deep, split across layers, sometimes as a *missing* check rather than a dangerous call.

| Repo | What it is |
|---|---|
| **ticketdesk-python** (this repo) | Realistic FastAPI target |
| [vulnlab-python-basics](https://github.com/karthikeyanchand/vulnlab-python-basics) / [vulnlab-js-basics](https://github.com/karthikeyanchand/vulnlab-js-basics) | Small warm-up targets |
| [vuln-scan-skill](https://github.com/karthikeyanchand/vuln-scan-skill) | The Codex agent skill that scans it |
| [vuln-scan-workshop](https://github.com/karthikeyanchand/vuln-scan-workshop) | Notebook that runs each stage and scores the results |

## What the app does

- **Organizations** (tenants) with **admins**, **agents** and **customers**
- **Tickets** with comments (public and internal), tags, priorities and assignees
- **Attachments**: upload, import from a URL, thumbnails, signed share links
- **Webhooks** for ticket and comment events, delivered by a background worker
- **Customisable email templates** per organization
- **Reports** (SLA by assignee, ticket volume), **CSV export**, **YAML import** from a legacy helpdesk
- **Customer portal**: server-rendered HTML pages using a cookie session
- **API keys** for integrations, and an **audit log**

## What's in the answer key

[`answer-key.json`](answer-key.json) contains **spoilers**, so run the scan first. It has four sections:

| Section | Count | Meaning |
|---|---|---|
| `vulnerabilities` | 18 | Real, verified bugs: access control, authentication, injection, deserialization and more. Each lists the main file, `also_accept` files along the same source → sink chain, CWE, line, severity and fix |
| `decoys` | 13 | Safe code that looks like a bug, often right next to the real one |
| `canaries` | 1 | A prompt injection aimed at AI reviewers, hidden in a code comment |
| `hardening` | 5 | Real hygiene gaps (missing controls, unsafe defaults), scored separately |

Every vulnerability, decoy and hardening item was verified by actually exercising it against a running instance, not just by reading the code.

The source contains no hint comments. Some comments explain design decisions the way real comments do, and some of those explanations are wrong. That's part of the exercise.

## Run it (optional)

Python 3.11+:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python seed.py                 # two demo orgs: acme and globex
uvicorn ticketdesk.main:app    # http://127.0.0.1:8000/docs
pytest -q                      # the app's own functional tests
```

Demo users are `admin@`, `agent@` and `cust@` at `acme.example.com` and `globex.example.com`. `seed.py` prints the shared demo password.

The webhook worker runs separately: `python -m ticketdesk.workers.dispatcher`.

## Layout

```
ticketdesk/
  main.py config.py database.py deps.py security.py
  models/        SQLAlchemy models (organization, user, ticket, comment, attachment, webhook, ...)
  schemas/       Pydantic request/response models
  repositories/  data access, including hand-written reporting SQL
  services/      business logic (tickets, comments, attachments, webhooks, imports, reports, ...)
  routers/       HTTP endpoints (auth, users, tickets, attachments, admin, reports, portal)
  workers/       background webhook dispatcher
  utils/         files, URLs, markdown, pagination
  templates/     portal HTML and email templates
tests/           functional tests (they pass; they don't test security)
Dockerfile  docker-compose.yml  seed.py  answer-key.json
```

## License

MIT, for education, with no warranty of any kind.
