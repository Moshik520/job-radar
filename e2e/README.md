# Browser tests

Selenium tests for the main flows (page objects in `selenium_tests/pages/`) and Playwright tests for error states
that need a mocked API. They run against a separate API and database, so they don't touch your real data:
the API on port 8001 with `MONGO_DB=job_radar_e2e`, and the app on port 4201. `conftest.py` fills that database
with the jobs in `test_data.py` before every run.

```bash
# terminal 1: API for the tests
cd backend
$env:MONGO_DB="job_radar_e2e"; $env:CORS_ORIGINS="http://localhost:4201"; uvicorn app.main:app --port 8001
# macOS/Linux: MONGO_DB=job_radar_e2e CORS_ORIGINS=http://localhost:4201 uvicorn app.main:app --port 8001

# terminal 2: the app, pointed at that API
cd frontend
npx ng serve --configuration e2e

# terminal 3: the tests
cd e2e
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
pytest -v
```

Set `HEADED=1` to watch the Selenium browser, or add `--headed` for Playwright.
