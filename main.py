"""A7 - Your first background job (Python lane: FastAPI + Inngest).

accept fast (202)  ->  work in the background (Inngest)  ->  report status (GET /reports/{id})
"""
import datetime
import logging
import os
import uuid
from collections import Counter

# Talk to the local Inngest Dev Server (no account, no keys).
os.environ.setdefault("INNGEST_DEV", "1")

import inngest
import inngest.fast_api
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("uvicorn")

# In-memory store: forgets everything on restart (on purpose, same lesson as A1).
reports: dict[str, dict] = {}

inngest_client = inngest.Inngest(app_id="report-api", logger=logger)


# ---------- Stage 1: first function (event-triggered) ----------
@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-a-bit", datetime.timedelta(seconds=5))
    return "Hello from the background!"


# ---------- Stages 2-3: the report job ----------
async def report_failed(ctx: inngest.Context) -> None:
    """Runs once, after the last retry has failed: mark the report as failed."""
    try:
        report_id = ctx.event.data["event"]["data"]["id"]
        if report_id in reports:
            reports[report_id]["status"] = "failed"
    except Exception:  # never let the failure handler itself blow up
        logger.exception("could not mark report as failed")


@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,  # 1 attempt + 2 retries = 3 attempts, then Failed
    on_failure=report_failed,
)
async def make_report(ctx: inngest.Context) -> dict:
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    # Idempotency: the same event twice must build the report only once.
    existing = reports.get(report_id)
    if existing and existing["status"] == "done":
        return existing

    # Step 1: stand-in for a slow task (AI call, big export...)
    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    # Step 2: build the result and save it
    def build_report() -> str:
        if topic == "fail":
            raise Exception("The report oven is broken!")
        result = f"Report about '{topic}': 3 key findings, 2 risks, 1 recommendation."
        reports[report_id].update(status="done", result=result)
        return result

    await ctx.step.run("build-report", build_report)
    return reports[report_id]


# ---------- Stage 4: cron job (the clock is the only trigger) ----------
@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),  # every minute - testing only
)
async def heartbeat(ctx: inngest.Context) -> dict:
    counts = Counter(r["status"] for r in reports.values())
    summary = {s: counts.get(s, 0) for s in ("pending", "done", "failed")}
    ctx.logger.info(
        f"heartbeat: {summary['pending']} pending, "
        f"{summary['done']} done, {summary['failed']} failed"
    )
    return summary


# ---------- The API ----------
app = FastAPI(title="Background job API")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reports")
async def create_report(request: Request):
    # Validate at the door: bad input is a 400, never a retry.
    try:
        body = await request.json()
    except Exception:
        body = None
    topic = body.get("topic") if isinstance(body, dict) else None
    if not isinstance(topic, str) or not topic.strip():
        return JSONResponse({"error": "topic is required"}, status_code=400)

    report_id = str(uuid.uuid4())
    reports[report_id] = {"id": report_id, "topic": topic, "status": "pending"}
    await inngest_client.send(
        inngest.Event(name="report/requested", data={"id": report_id, "topic": topic})
    )
    # No slow work here - that is the whole point.
    return JSONResponse({"id": report_id, "status": "pending"}, status_code=202)


@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    report = reports.get(report_id)
    if report is None:
        return JSONResponse({"error": "report not found"}, status_code=404)
    return report


@app.get("/reports")  # extra: the "control panel"
async def list_reports():
    return list(reports.values())


# Serve the Inngest functions at /api/inngest
inngest.fast_api.serve(
    app, inngest_client, [say_hello, make_report, heartbeat]
)
