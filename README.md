# Background Job API (FlyRank A7)

A small FastAPI service whose slow work (an 8-second "report") runs in a **background job** powered by [Inngest](https://www.inngest.com). The endpoint answers instantly with `202`, a status endpoint reports progress, and one **cron job** runs on the clock alone.

Pattern: **accept fast -> work in the background -> report status.**

## Run it (Python 3.10+)

```bash
# one-time setup
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

Terminal 1 - the API (port 8000):
```bash
uvicorn main:app --port 8000
```

Terminal 2 - the Inngest Dev Server + dashboard (no account needed, needs Node.js):
```bash
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```

Dashboard: http://localhost:8288

## Endpoints and functions

| Kind | Name | Trigger | What it does |
|---|---|---|---|
| Endpoint | `GET /health` | request | `{"status":"ok"}` |
| Endpoint | `POST /reports` | request | validates `topic` (missing -> **400**), saves `pending`, sends `report/requested`, returns **202** + id |
| Endpoint | `GET /reports/{id}` | request | `pending` -> `done` (+ result) / `failed`; unknown id -> **404** |
| Endpoint | `GET /reports` | request | extra: lists all reports |
| Function | `say-hello` | event `test/hello` | sleeps 5 s, returns "Hello from the background!" |
| Function | `make-report` | event `report/requested` | step `do-the-slow-work` (sleep 8 s) + step `build-report`; `retries=2`; topic `"fail"` always errors; idempotent (a report already `done` is not rebuilt) |
| Function | `heartbeat` | cron `* * * * *` | logs `heartbeat: N pending, N done, N failed` |

## Proof (real run)

```text
$ curl -i -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d '{"topic":"cats"}'
HTTP 202 in 0.0087 s
{"id":"bdb52923-a137-4fac-b7cd-230801998126","status":"pending"}

$ curl http://localhost:8000/reports/bdb52923-a137-4fac-b7cd-230801998126      # right away
{"id":"bdb52923-...","topic":"cats","status":"pending"}

$ curl http://localhost:8000/reports/bdb52923-a137-4fac-b7cd-230801998126      # ~12 s later
{"id":"bdb52923-...","topic":"cats","status":"done","result":"Report about 'cats': 3 key findings, 2 risks, 1 recommendation."}

$ curl -X POST .../reports -d '{}'            -> HTTP 400 {"error":"topic is required"}
$ curl .../reports/nope                       -> HTTP 404 {"error":"report not found"}
```

A `topic: "fail"` report: attempt 1 fails -> backoff -> attempt 2 -> attempt 3 -> run ends **Failed**, and the report status becomes `failed`.

![Inngest dashboard](dashboard.png)
<!-- TODO: save your own dashboard screenshot as dashboard.png (make-report completed, a failed run with 3 attempts, heartbeat runs) -->

## Stage 3 - retry vs. validation

A missing `topic` is a *wrong input*, so it is rejected at the door with a 400 and never becomes a job; a retry only helps when the *moment* was wrong (network drop, flaky service), because running the same bad input again can never succeed.

## Stage 4 - cron expressions

- Every day at 08:00: `0 8 * * *`
- Every Sunday at 22:00: `0 22 * * 0`

(The heartbeat runs every minute, `* * * * *`, for testing only; a real one would be daily.)

## Extras / stretch

- `GET /reports` list endpoint.
- Idempotency: `make-report` returns early if the report is already `done`, so a duplicate `report/requested` event with the same id builds it once. Jobs must survive running twice because queues deliver at-least-once (retries, restarts, duplicate sends), so the effect has to happen once no matter how many times the job runs.

## Notes

- State is in-memory on purpose: restarting the API forgets all reports.
- `INNGEST_DEV=1` is set in `main.py`, so no env setup is needed for the Dev Server.
