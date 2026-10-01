# Background Job API & Personal Study Coach (FlyRank Capstone)

A robust FastAPI service whose slow work (an 8-second "report") runs in a **background job** powered by [Inngest](https://www.inngest.com). The endpoint answers instantly with `202`, a status endpoint reports progress, and a cron job runs on the clock. It is paired with an AI Study Coach agent workspace.

Pattern: **accept fast -> work in the background -> report status.**

## Run it (Python 3.10+)

```bash
# one-time setup
python -m venv .venv
.venv\Scripts\activate         # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt