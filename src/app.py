"""
FastAPI web app — exposes the calculator as a simple web UI.

Key differences from Flask:
- Routes are async functions
- Form data requires python-multipart and FastAPI's Form()
- Templates need 'request' passed explicitly in the context
- Run with uvicorn, not the built-in dev server

Monitoring:
- prometheus-fastapi-instrumentator auto-instruments all routes
- Metrics are exposed at /metrics (scraped by Prometheus every 15s)
- Grafana reads from Prometheus to render dashboards
"""

from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator
from calculator import add, subtract, multiply, divide

app = FastAPI(title="CI/CD Calculator")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

# Instrument all routes and expose /metrics endpoint
Instrumentator().instrument(app).expose(app)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"result": None, "error": None}
    )


@app.post("/", response_class=HTMLResponse)
async def calculate(
    request: Request,
    a: float = Form(...),
    b: float = Form(...),
    operation: str = Form(...),
):
    result = None
    error = None

    try:
        if operation == "add":
            result = add(a, b)
        elif operation == "subtract":
            result = subtract(a, b)
        elif operation == "multiply":
            result = multiply(a, b)
        elif operation == "divide":
            result = divide(a, b)
    except ValueError as e:
        error = str(e)

    return templates.TemplateResponse(request, "index.html", {"result": result, "error": error})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
