# Python Calculator - fastapi-calculator-devops-pipeline

![CI Pipeline](https://github.com/earthinversion/CICD_workflow/actions/workflows/ci.yml/badge.svg)

I built this project to learn and demonstrate a complete **Dev → CI → Monitor** workflow
using real industry tools. I kept the application intentionally simple (a calculator)
so I could focus on understanding the pipeline rather than getting lost in the code.

---

## What I Built and Why

I mapped this project directly to both halves of the DevOps infinity loop:

```
PLAN → CODE → BUILD → TEST → INTEGRATE → MONITOR
```

| Phase | Tool I Used | How I applied it |
|-------|-------------|-----------------|
| Plan | (this README) | Decided the app scope: a FastAPI calculator |
| Code | Git | Version-controlled from the very first commit |
| Build | Makefile + pip | `make install` installs all dependencies |
| Test | pytest + Selenium | Unit tests covering the logic + browser UI tests |
| Integrate | Jenkins + GitHub Actions | Two CI options — local Jenkins and cloud GitHub Actions |
| Monitor | Prometheus + Grafana | Metrics scraped from `/metrics`, visualised in live dashboards |

---

## Project Structure

```
CICD_workflow/
├── src/
│   ├── calculator.py       # Core math logic (pure Python, no dependencies)
│   └── app.py              # FastAPI web server + Prometheus instrumentation
├── templates/
│   └── index.html          # Simple HTML UI for the calculator
├── tests/
│   ├── test_calculator.py  # pytest unit tests (11 tests)
│   └── test_selenium.py    # Selenium browser UI tests
├── monitoring/
│   ├── prometheus.yml      # Prometheus scrape config (targets the FastAPI app)
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── prometheus.yml   # Auto-connects Grafana to Prometheus
│           └── dashboards/
│               ├── dashboard.yml    # Dashboard loader config
│               └── calculator.json  # Pre-built dashboard (5 panels)
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions pipeline (cloud CI alternative to Jenkins)
├── Dockerfile              # Packages the FastAPI app as a container
├── docker-compose.yml      # Runs app + Prometheus + Grafana together
├── Makefile                # Build commands — replaces Maven/Gradle for Python
├── Jenkinsfile             # Declarative Jenkins CI pipeline (local CI)
├── requirements.txt        # Python dependencies
└── .gitignore
```

---

## The Application

I built a simple web-based calculator using **FastAPI**. I chose FastAPI over Flask
because it is the modern standard for Python web APIs — it is async-first, faster,
and generates interactive API docs out of the box.

FastAPI key properties:
- **Fast** — one of the fastest Python frameworks available, built on Starlette and Pydantic
- **Async-first** — routes are defined as `async` functions using Python's `asyncio`
- **Self-documenting** — automatically generates interactive API docs at `/docs`
- **Type-safe** — uses Python type hints to validate inputs automatically

The app:
- Supports addition, subtraction, multiplication, and division
- Handles divide-by-zero gracefully with a user-friendly error message
- Runs locally at `http://localhost:5000`
- Exposes interactive API docs at `http://localhost:5000/docs`

### Core Logic — `src/calculator.py`

I wrote four pure functions with no external dependencies:

```python
add(a, b)        # returns a + b
subtract(a, b)   # returns a - b
multiply(a, b)   # returns a * b
divide(a, b)     # returns a / b  — raises ValueError if b == 0
```

Keeping the logic completely separate from the web layer made it easy to
unit-test without starting the server at all.

### Web Layer — `src/app.py`

The FastAPI app has two routes on `/`:

- `GET /` — serves the HTML form
- `POST /` — receives form data using FastAPI's `Form()`, calls the relevant
  calculator function, and renders the result back in the template

```python
@app.post("/", response_class=HTMLResponse)
async def calculate(
    request: Request,
    a: float = Form(...),       # FastAPI parses and validates this automatically
    b: float = Form(...),
    operation: str = Form(...),
):
```

I run the app with **uvicorn**, an ASGI server — the standard way to serve FastAPI.

### UI — `templates/index.html`

A plain HTML form with two number inputs, a dropdown to select the operation,
a submit button, and a result/error display area. I also used the element IDs
(`result`, `error`) as hooks for the Selenium tests to verify the output.

---

## Phase 1 — PLAN

My plan was to build the simplest possible app that still exercises every tool
in the pipeline. I chose a calculator because:

- The logic is trivial and easy to follow
- It has clear inputs and outputs — perfect for unit testing
- A form-based UI makes Selenium tests straightforward to write
- It needs no database or external APIs

---

## Phase 2 — CODE (Git)

I use Git for version control from the very first line of code. Every meaningful
change gets its own commit with a clear message.

### Setup

```bash
git init
git add .
git commit -m "Initial commit"
```

### My commit workflow

Every change I make follows this cycle:

```bash
# 1. Edit the code
# 2. Stage the specific file(s)
git add src/calculator.py

# 3. Write a clear commit message
git commit -m "Add modulo operation to calculator"

# 4. Push — this triggers Jenkins automatically
git push origin main
```

### Why Git is central to CI/CD

Jenkins watches the Git repository. Every `git push` I make automatically
triggers the Jenkins pipeline — that is what "Continuous Integration" means.
No manual steps, no human error in between.

---

## Phase 3 — BUILD (Makefile + pip)

In Java projects, Maven or Gradle handle the build. For Python, I use a
`Makefile` combined with `pip` to get the same result.

### Commands I use

| Command | What it does |
|---------|-------------|
| `make install` | Installs all dependencies from `requirements.txt` |
| `make run` | Starts the FastAPI app at `http://localhost:5000` |
| `make test-unit` | Runs only the fast unit tests |
| `make test-ui` | Runs the Selenium browser tests |
| `make test` | Runs all tests |
| `make monitor` | Starts the full stack (app + Prometheus + Grafana) via Docker |
| `make monitor-down` | Stops and removes all Docker containers |
| `make clean` | Removes `__pycache__`, `.pyc` files, and `.pytest_cache` |

### Dependencies — `requirements.txt`

```
fastapi>=0.100                         # Modern async web framework
uvicorn[standard]>=0.23                # ASGI server to run FastAPI
python-multipart>=0.0.6                # Required for parsing HTML form data
jinja2>=3.0                            # HTML templating engine
prometheus-fastapi-instrumentator>=6.0 # Auto-instruments FastAPI for Prometheus
pytest>=7.0                            # Test runner
selenium>=4.0                          # Browser automation for UI tests
```

Install everything with:

```bash
make install
# or directly:
pip install -r requirements.txt
```

---

## Phase 4 — TEST (pytest + Selenium)

I split testing into two layers. The idea is to run fast tests first and only
run slow browser tests after the logic is confirmed correct.

### Layer 1: Unit Tests — `tests/test_calculator.py`

I test the core logic in complete isolation — no browser, no network, no
FastAPI. Just Python functions. These run in under a second.

**11 tests across 4 classes:**

| Class | Tests I wrote |
|-------|--------------|
| `TestAdd` | positive numbers, negative numbers, mixed signs, floats |
| `TestSubtract` | basic subtraction, negative result |
| `TestMultiply` | basic multiplication, multiply by zero |
| `TestDivide` | basic division, float result, divide by zero error |

```bash
make test-unit
```

Expected output:

```
pytest tests/test_calculator.py -v
=================================================== test session starts ===================================================
platform darwin -- Python 3.11.11, pytest-9.0.2, pluggy-1.5.0 -- /Users/utpalkumar/miniconda3/bin/python3.11
cachedir: .pytest_cache
rootdir: /Users/utpalkumar/Documents/datascience/CICD_workflow
plugins: anyio-4.12.1, mock-3.15.1, cov-7.0.0
collected 11 items                                                                                                        

tests/test_calculator.py::TestAdd::test_positive_numbers PASSED                                                     [  9%]
tests/test_calculator.py::TestAdd::test_negative_numbers PASSED                                                     [ 18%]
tests/test_calculator.py::TestAdd::test_mixed PASSED                                                                [ 27%]
tests/test_calculator.py::TestAdd::test_floats PASSED                                                               [ 36%]
tests/test_calculator.py::TestSubtract::test_basic PASSED                                                           [ 45%]
tests/test_calculator.py::TestSubtract::test_negative_result PASSED                                                 [ 54%]
tests/test_calculator.py::TestMultiply::test_basic PASSED                                                           [ 63%]
tests/test_calculator.py::TestMultiply::test_by_zero PASSED                                                         [ 72%]
tests/test_calculator.py::TestDivide::test_basic PASSED                                                             [ 81%]
tests/test_calculator.py::TestDivide::test_float_result PASSED                                                      [ 90%]
tests/test_calculator.py::TestDivide::test_divide_by_zero PASSED                                                    [100%]

=================================================== 11 passed in 0.02s ====================================================
```

### Layer 2: UI Tests — `tests/test_selenium.py`

I test the full application through a real browser (headless Chrome). Selenium
fills in the form, clicks the button, and checks what appears on screen — the
same way an actual user would interact with it.

**3 UI tests I wrote:**

| Test | What it does |
|------|-------------|
| `test_page_loads` | Opens the app and confirms the title says "Calculator" |
| `test_addition` | Enters 10 + 5, submits the form, checks that "15" appears |
| `test_division_by_zero` | Enters 10 ÷ 0, submits, checks the error message mentions "zero" |

**How it works internally:**

1. A pytest fixture starts the FastAPI app via uvicorn in a background thread on port 5001
2. Another fixture launches headless Chrome via `webdriver.Chrome`
3. Each test navigates to `http://localhost:5001`, interacts with the form, and
   asserts on what appears in the HTML
4. When all tests finish, the browser and server shut down automatically

**Prerequisites:**

```bash
# Install chromedriver (must match the installed Chrome version)
brew install chromedriver

make test-ui
```

> If the `selenium` package is not installed, these tests skip automatically,
> so `make test` is always safe to run.

---

## Phase 5 — INTEGRATE (Jenkins)

Jenkins is the CI server. It reads the `Jenkinsfile` I wrote and runs the full
pipeline automatically on every `git push`.

### Install Jenkins (macOS)

```bash
brew install jenkins-lts
brew services start jenkins-lts
```

Then open `http://localhost:8080` and complete the initial setup wizard.

### My Pipeline — `Jenkinsfile`

I structured the pipeline into 5 stages:

```
Stage 1: Code Checkout
    └── Jenkins checks out the Git repo and prints branch/commit info

Stage 2: Build
    └── Creates a Python virtual environment (.venv)
    └── Runs: pip install -r requirements.txt

Stage 3: Unit Tests
    └── Runs: pytest tests/test_calculator.py -v --tb=short
    └── If any test fails, the build is marked FAILED and stops here

Stage 4: UI Tests
    └── Runs: pytest tests/test_selenium.py -v --tb=short
    └── Skipped gracefully if Selenium/Chrome is not available on the agent

Stage 5: Integration Complete
    └── Prints "All checks passed. Ready to deploy!"
    └── This is where a Deploy stage would be added next
```

### Connecting Jenkins to this repo

1. Open Jenkins at `http://localhost:8080`
2. Click **New Item** → name it `calculator-pipeline` → choose **Pipeline**
3. Under **Pipeline**, set **Definition** to `Pipeline script from SCM`
4. Set **SCM** to `Git` and paste the repository URL
5. Set **Script Path** to `Jenkinsfile`
6. Click **Save**, then **Build Now**

Each stage turns green (or red) in the Stage View after the run.

### Triggering automatically on every push

To have Jenkins pick up every `git push` automatically:

1. In Jenkins → the job → **Configure** → **Build Triggers**
2. Check **Poll SCM** and set the schedule to `* * * * *` (polls every minute)
3. Or configure a webhook from GitHub/GitLab pointing to `http://<jenkins-host>/github-webhook/`

---

## Phase 5b — INTEGRATE with GitHub Actions (Cloud CI)

GitHub Actions is GitHub's native CI system. It does exactly what Jenkins does,
but runs in the cloud with zero server setup — making it the more practical choice
for any project already hosted on GitHub.

### Jenkins vs GitHub Actions — when I'd use each

| | Jenkins | GitHub Actions |
|---|---------|---------------|
| Where it runs | My local machine (or a server I manage) | GitHub's cloud servers — free |
| Setup effort | Install, configure, maintain | Just push a YAML file |
| Trigger on push | Needs polling or ngrok for local setup | Works natively, instantly |
| Selenium/Chrome | Needs chromedriver on the Jenkins agent | Pre-installed on `ubuntu-latest` |
| Best for | Teams with dedicated CI infrastructure | Projects hosted on GitHub |

For this project I included both so I can see the same pipeline expressed in
two different systems side by side.

### My GitHub Actions Pipeline — `.github/workflows/ci.yml`

The workflow triggers automatically on every push to `main` and on every pull request.
It is structured as three jobs that mirror the Jenkinsfile stages exactly:

```
Job 1: Build & Unit Tests          → runs first, always
Job 2: UI Tests (Selenium/Chrome)  → runs only if Job 1 passes
Job 3: Integration Complete        → runs only if both jobs are green
```

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

**Why separate jobs instead of one?**
If unit tests fail, GitHub skips the slower Selenium job entirely. Fast feedback,
no wasted compute time.

**How Selenium works in GitHub Actions:**
The `ubuntu-latest` runner has Chrome pre-installed. The `browser-actions/setup-chrome@v1`
step ensures the ChromeDriver version matches Chrome exactly — the same problem
`brew install chromedriver` solves locally.

```yaml
- name: Set up Chrome
  uses: browser-actions/setup-chrome@v1
  with:
    chrome-version: stable
```

**Pip caching:**
Both jobs use `cache: "pip"` in the Python setup step. GitHub caches the downloaded
packages between runs, so repeated builds are significantly faster.

### Status badge

After pushing to GitHub, the pipeline status appears as a badge at the top of
this README. Replace `<your-username>` in the badge URL with the actual GitHub username:

```
![CI Pipeline](https://github.com/<your-username>/CICD_workflow/actions/workflows/ci.yml/badge.svg)
```

### How to activate it

The workflow runs automatically the moment the repo is pushed to GitHub — no
configuration needed. GitHub detects `.github/workflows/ci.yml` and starts
running it on every push.

To see results: GitHub repo → **Actions** tab → **CI Pipeline**.

---

## Phase 6 — MONITOR (Prometheus + Grafana)

Monitoring answers the question: **"Is the app healthy right now?"**
Unlike tests which run at build time, monitoring runs continuously in production.

### Why I chose Prometheus + Grafana over Nagios

Nagios checks if a server is reachable (ping-style uptime checks). Prometheus
goes deeper — it collects *what the app is actually doing*: request rates,
latency distributions, error percentages. Grafana visualises all of that in
live dashboards. Together they are the industry-standard open-source monitoring
stack for modern Python web apps.

### How the data flows

```
FastAPI app          Prometheus              Grafana
    │                    │                     │
    │  every 15s         │                     │
    │◄── GET /metrics ───│                     │
    │─── metrics data ──►│                     │
    │                    │◄── PromQL query ────│
    │                    │─── time-series ────►│
    │                    │                     │── renders dashboard
```

1. `prometheus-fastapi-instrumentator` adds a `/metrics` endpoint to the app automatically
2. Prometheus scrapes it every 15 seconds and stores the data as time-series
3. Grafana queries Prometheus using PromQL and renders the live panels

### Metrics collected automatically

| Metric | Type | What it tells me |
|--------|------|-----------------|
| `http_requests_total` | Counter | Total requests by method, route, status code |
| `http_request_duration_seconds` | Histogram | How long each request took |
| `http_request_size_bytes` | Histogram | Size of incoming requests |
| `http_response_size_bytes` | Histogram | Size of outgoing responses |

### My Grafana Dashboard — `monitoring/grafana/provisioning/dashboards/calculator.json`

I pre-built the dashboard so it loads automatically when Grafana starts — no
manual setup needed. It has 5 panels:

| Panel | PromQL Query | What I look for |
|-------|-------------|----------------|
| Request Rate (req/sec) | `rate(http_requests_total[1m])` | Spikes = traffic surge |
| Error Rate (%) | `rate(status 4xx+5xx) / rate(all)` | Should stay at 0% |
| Latency p50 / p95 / p99 | `histogram_quantile(...)` | p99 spike = slow outliers |
| Total Requests (all time) | `sum(http_requests_total)` | Cumulative counter |
| Requests by Operation | POST requests grouped by handler | Which operation is used most |

### Prerequisites

Docker must be installed:

```bash
brew install --cask docker
open /Applications/Docker.app   # start Docker Desktop
```

### Starting the monitoring stack

```bash
make monitor
```

This runs `docker compose up --build -d`, which:
1. Builds the FastAPI app into a Docker image using the `Dockerfile`
2. Starts three containers: `calculator-app`, `prometheus`, `grafana`

After ~10 seconds everything is up:

| Service | URL | Notes |
|---------|-----|-------|
| Calculator app (Docker) | `http://localhost:5001` | Port 5001 avoids conflict with `make run` on 5000 |
| Raw metrics | `http://localhost:5001/metrics` | — |
| Prometheus UI | `http://localhost:9090` | — |
| Grafana dashboards | `http://localhost:3000` | Login: admin / admin |

### Viewing the dashboard

1. Open `http://localhost:3000`, log in with `admin` / `admin`
2. Click **Dashboards** in the left sidebar
3. Open **Calculator** folder → **Calculator App — CI/CD Monitor**
4. Use the app at `http://localhost:5001` to generate traffic — panels refresh every 10 seconds

### Exploring raw metrics in Prometheus

I open `http://localhost:9090` and run PromQL queries directly:

```promql
# Request rate over the last minute
rate(http_requests_total[1m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[1m]))

# Error rate as a percentage
rate(http_requests_total{status_code=~"4..|5.."}[1m])
  / rate(http_requests_total[1m]) * 100
```

### Stopping the stack

```bash
make monitor-down
```

---

## Quick Start

```bash
# 1. Install dependencies
make install

# 2. Run the app locally (no Docker needed)
make run
# App:      http://localhost:5000
# API docs: http://localhost:5000/docs

# 3. Run unit tests
make test-unit

# 4. Run all tests (Selenium tests skip if Chrome is not set up)
make test

# 5. Start the full monitoring stack (requires Docker)
make monitor
# App (Docker) → http://localhost:5001  (5000 kept free for make run)
# Prometheus   → http://localhost:9090
# Grafana      → http://localhost:3000  (admin / admin)

# 6. Stop the monitoring stack
make monitor-down

# 7. Clean up build artifacts
make clean
```

---

## Tools Summary

| Tool | Category | How I use it |
|------|----------|-------------|
| **Git** | Code | Version control; every push triggers Jenkins |
| **pip** | Build | Installs Python packages from `requirements.txt` |
| **Makefile** | Build | Single entry point for all build, test, and monitor commands |
| **FastAPI** | Framework | Async web framework that serves the calculator UI |
| **uvicorn** | Server | ASGI server that runs the FastAPI app |
| **Jinja2** | Templates | Renders the HTML calculator form |
| **pytest** | Test | Runs 11 unit tests covering all calculator functions |
| **Selenium** | Test | Browser automation — tests the UI end-to-end |
| **Jenkins** | CI | Local CI server; pipeline defined in `Jenkinsfile` |
| **GitHub Actions** | CI | Cloud CI; pipeline defined in `.github/workflows/ci.yml` |
| **Docker** | Monitor | Packages app + monitoring stack into containers |
| **Prometheus** | Monitor | Scrapes `/metrics` every 15s and stores time-series data |
| **Grafana** | Monitor | Queries Prometheus and renders live dashboards |

---

## What I Plan to Add Next

I've covered the full DEV + MONITOR loop. The remaining OPS phases I want to explore:

| Phase | Tool | What I plan to do |
|-------|------|------------------|
| Deploy | Ansible | Automate deployment of the Docker containers to a remote server |
| Operate | Kubernetes | Replace docker-compose with a K8s cluster for production-grade orchestration |
