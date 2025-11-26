import os
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pytest
from dotenv import load_dotenv
from py.xml import html  # type: ignore
from pytest_html import extras
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ServiceChrome
from selenium.webdriver.firefox.service import Service as ServiceFirefox
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from utils.config import load_settings

RUN_STATS: Dict[str, object] = {
    "start": None,
    "end": None,
    "counts": {"passed": 0, "failed": 0, "skipped": 0, "error": 0},
    "duration": 0.0,
}

CUSTOM_CSS = """
body {font-family: 'Inter','Segoe UI','Helvetica Neue',Arial,sans-serif; background:#0c1220; color:#e5e7eb; margin:0; padding:18px;}
a {color:#38bdf8;}
#environment {display:none;}
.report-header {background:radial-gradient(circle at 10% 20%,rgba(99,102,241,0.35),transparent 30%),linear-gradient(135deg,#0ea5e9,#6366f1); color:#fff; padding:18px 22px; border-radius:18px; margin-bottom:18px; box-shadow:0 14px 28px rgba(0,0,0,0.3);}
.report-title {margin:0; font-size:26px; font-weight:800; letter-spacing:0.2px;}
.report-subtitle {margin:8px 0 14px; color:rgba(255,255,255,0.92);}
.report-meta {display:flex; gap:10px; flex-wrap:wrap;}
.meta-chip {background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); padding:7px 11px; border-radius:12px; font-size:12px;}
.summary-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px; margin:12px 0 18px;}
.summary-card {background:#0f172a; border:1px solid #1f2937; padding:12px 14px; border-radius:12px; box-shadow:0 12px 24px rgba(0,0,0,0.22);}
.summary-card .label {font-size:12px; color:#94a3b8; margin-bottom:4px;}
.summary-card .value {font-size:15px; font-weight:700; color:#e2e8f0;}
.status-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin:12px 0 14px;}
.stat-card {background:linear-gradient(145deg,#0d1628,#0f172a); border:1px solid #1f2937; border-left:6px solid #38bdf8; padding:12px 14px; border-radius:12px; display:flex; justify-content:space-between; align-items:flex-end; box-shadow:0 12px 22px rgba(0,0,0,0.24);}
.stat-card .label {font-size:12px; color:#94a3b8;}
.stat-card .value {font-size:20px; font-weight:800; color:#e2e8f0;}
.stat-card .sub {font-size:12px; color:#9ca3af;}
.stat-card.passed {border-left-color:#22c55e;}
.stat-card.failed {border-left-color:#ef4444;}
.stat-card.skipped {border-left-color:#facc15;}
.stat-card.error {border-left-color:#fb923c;}
#summary {display:none;}
#results-table {width:100%; border-collapse:collapse; overflow:hidden; border-radius:14px; box-shadow:0 16px 30px rgba(0,0,0,0.28);}
#results-table th {background:#0f172a; color:#e5e7eb; padding:11px; border:1px solid #1f2937; text-align:left;}
#results-table td {padding:10px 11px; border:1px solid #1f2937; background:#0b1323;}
#results-table tr:nth-child(even) td {background:#0d152a;}
#results-table tr:hover td {background:#111a2f;}
.status-badge {padding:6px 12px; border-radius:999px; font-size:12px; font-weight:800; text-transform:capitalize; letter-spacing:0.2px;}
.status-badge.passed {background:#16a34a1a; color:#22c55e; border:1px solid #14532d;}
.status-badge.failed {background:#ef44441a; color:#ef4444; border:1px solid #7f1d1d;}
.status-badge.error {background:#f973161a; color:#fb923c; border:1px solid #c2410c;}
.status-badge.skipped {background:#eab3081a; color:#facc15; border:1px solid #854d0e;}
.col-description {max-width:420px;}
.evidence {display:flex; gap:10px; flex-wrap:wrap;}
.evidence-item {background:#0f172a; border:1px solid #1f2937; border-radius:12px; padding:8px; display:flex; align-items:center; gap:8px; box-shadow:0 8px 16px rgba(0,0,0,0.2);}
.evidence-item img {height:68px; width:auto; border-radius:10px; border:1px solid #1f2937; object-fit:cover;}
.evidence-label {font-size:12px; color:#e2e8f0; font-weight:600;}
.muted {color:#9ca3af;}
"""

load_dotenv()
os.environ["WDM_LOG_LEVEL"] = "0"
warnings.filterwarnings(
    "ignore",
    message=".*'urllib3\\[secure\\]' extra is deprecated.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message="HTTPResponse.getheader\\(\\) is deprecated.*",
    category=DeprecationWarning,
    module="selenium.webdriver.remote.remote_connection",
)


@pytest.fixture(scope="session")
def settings():
    """Settings loaded once per session from data/config.yaml."""
    return load_settings()


@pytest.fixture(scope="session")
def credentials():
    """Credentials provided via environment variables."""
    return {
        "username": os.getenv("USERNAME", ""),
        "password": os.getenv("PASSWORD", ""),
        "invalid_password": os.getenv("FAIL_PASSWORD", "invalid-password"),
    }


def pytest_sessionstart(session):
    RUN_STATS["start"] = datetime.now()


def pytest_sessionfinish(session, exitstatus):
    RUN_STATS["end"] = datetime.now()


def _build_driver(settings):
    browser = settings["browser"].lower()
    headless = settings.get("headless", False)

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
        return webdriver.Chrome(service=ServiceChrome(ChromeDriverManager().install()), options=options)

    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        if headless:
            options.add_argument("--headless")
        return webdriver.Firefox(service=ServiceFirefox(GeckoDriverManager().install()), options=options)

    raise ValueError(f"Unsupported browser: {browser}")


@pytest.fixture
def driver(settings):
    warnings.filterwarnings("ignore", category=ResourceWarning)
    browser_driver = _build_driver(settings)
    browser_driver.maximize_window()
    yield browser_driver
    browser_driver.quit()


@pytest.fixture
def wait(driver, settings):
    return WebDriverWait(driver, settings.get("wait_timeout", 10))


def pytest_configure(config):
    """Add useful metadata to the HTML report."""
    settings = load_settings()
    metadata = getattr(config, "_metadata", {})
    metadata.update(
        {
            "Base URL": settings["base_url"],
            "Browser": settings["browser"],
            "Headless": settings["headless"],
            "Wait timeout (s)": settings["wait_timeout"],
            "Report generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    config._metadata = metadata

    reports_dir = Path("results")
    reports_dir.mkdir(exist_ok=True)


def pytest_html_report_title(report):
    report.title = "Selenium UI Test Report"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach description and screenshots to the HTML report."""
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__ or "").strip()

    if report.when != "call":
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    extra = getattr(report, "extra", [])
    current_url = None
    try:
        current_url = driver.current_url
    except Exception:
        current_url = None

    if report.failed:
        screenshot_base64 = driver.get_screenshot_as_base64()
        extra.append(extras.image(screenshot_base64, "base64", "Captura al fallar"))
        if current_url:
            extra.append(extras.url(current_url, name="URL al fallar"))
            extra.append(extras.text(f"Título: {driver.title}", name="Página"))

    report.extra = extra


def pytest_runtest_logreport(report):
    """Acumula estadísticas de ejecución para el resumen visual."""
    if report.when == "call":
        _increment_outcome(report)
        RUN_STATS["duration"] = float(RUN_STATS.get("duration", 0.0)) + float(getattr(report, "duration", 0.0))
    elif report.when == "setup":
        if report.skipped:
            _increment("skipped")
        elif report.failed:
            _increment("error")


def pytest_html_results_table_header(cells):
    cells[0] = html.th("Resultado")
    cells.insert(1, html.th("Descripción"))
    cells[2] = html.th("Prueba")
    cells[3] = html.th("Duración")
    cells.append(html.th("Evidencia"))


def pytest_html_results_table_row(report, cells):
    cells[0] = html.td(_status_badge(report), class_="col-result")
    cells.insert(1, html.td(report.description, class_="col-description"))
    cells.append(html.td(_evidence_cell(report), class_="col-evidence"))


def pytest_html_results_summary(prefix, summary, postfix):
    """Add a compact resumen de entorno al inicio del reporte."""
    settings = load_settings()
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hero = html.div(
        [
            html.h1("Selenium UI Test Report", class_="report-title"),
            html.p("Ejecución automatizada de UI con Selenium + Pytest", class_="report-subtitle"),
            html.div(
                [
                    html.span(f"Base URL: {settings['base_url']}", class_="meta-chip"),
                    html.span(f"Navegador: {settings['browser']}", class_="meta-chip"),
                    html.span(f"Headless: {settings['headless']}", class_="meta-chip"),
                    html.span(f"Timeout: {settings['wait_timeout']}s", class_="meta-chip"),
                    html.span(f"Generado: {generated}", class_="meta-chip"),
                ],
                class_="report-meta",
            ),
        ],
        class_="report-header",
    )
    prefix[0:0] = [
        html.style(CUSTOM_CSS),
        hero,
        _build_status_cards(),
        _build_env_cards(settings),
    ]


def _status_badge(report):
    if getattr(report, "failed", False):
        outcome = "failed"
    elif getattr(report, "skipped", False):
        outcome = "skipped"
    elif getattr(report, "passed", False):
        outcome = "passed"
    else:
        outcome = getattr(report, "outcome", "unknown").lower()
    label_map = {
        "passed": "Aprobada",
        "failed": "Falló",
        "skipped": "Omitida",
        "error": "Error",
    }
    label = label_map.get(outcome, outcome.title())
    return html.span(label, class_=f"status-badge {outcome}")


def _evidence_cell(report):
    items: List = []
    for extra in getattr(report, "extra", []):
        extra_format = extra.get("format")
        name = (extra.get("name") or extra_format or "").strip() or "Extra"
        content = extra.get("content")

        if extra_format == "image" and content:
            image = html.img(src=content, alt=name)
            items.append(
                html.div(
                    [html.a(image, href=content, target="_blank"), html.span(name, class_="evidence-label")],
                    class_="evidence-item image",
                )
            )
        elif extra_format == "url" and content:
            items.append(
                html.div(
                    [html.span("Link", class_="evidence-label"), html.a(name, href=content, target="_blank", class_="meta-chip")],
                    class_="evidence-item link",
                )
            )
        elif extra_format == "text" and content:
            items.append(html.div([html.span(name, class_="evidence-label"), html.span(content, class_="meta-chip")], class_="evidence-item text"))

    if not items:
        return html.span("Sin adjuntos", class_="muted")

    return html.div(items, class_="evidence")


def _increment_outcome(report):
    if report.passed:
        _increment("passed")
    elif report.failed:
        _increment("failed")
    elif report.skipped:
        _increment("skipped")


def _increment(key: str):
    RUN_STATS["counts"][key] = RUN_STATS["counts"].get(key, 0) + 1


def _build_status_cards():
    counts = RUN_STATS["counts"]
    total = sum(counts.values())
    duration = RUN_STATS.get("duration", 0.0)
    wall_clock = None
    if RUN_STATS.get("start") and RUN_STATS.get("end"):
        wall_clock = (RUN_STATS["end"] - RUN_STATS["start"]).total_seconds()

    cards = [
        html.div(
            [html.div("Aprobadas", class_="label"), html.div(str(counts.get("passed", 0)), class_="value")],
            class_="stat-card passed",
        ),
        html.div(
            [html.div("Fallidas", class_="label"), html.div(str(counts.get("failed", 0)), class_="value")],
            class_="stat-card failed",
        ),
        html.div(
            [html.div("Errores", class_="label"), html.div(str(counts.get("error", 0)), class_="value")],
            class_="stat-card error",
        ),
        html.div(
            [html.div("Omitidas", class_="label"), html.div(str(counts.get("skipped", 0)), class_="value")],
            class_="stat-card skipped",
        ),
        html.div(
            [
                html.div("Duración total", class_="label"),
                html.div(f"{duration:.2f}s", class_="value"),
                html.div("Reloj: " + (f"{wall_clock:.2f}s" if wall_clock else "N/D"), class_="sub"),
            ],
            class_="stat-card",
        ),
        html.div(
            [html.div("Total", class_="label"), html.div(str(total), class_="value")],
            class_="stat-card",
        ),
    ]
    return html.div(cards, class_="status-grid")


def _build_env_cards(settings):
    return html.div(
        [
            html.div([html.div("Base URL", class_="label"), html.div(settings["base_url"], class_="value")], class_="summary-card"),
            html.div([html.div("Navegador", class_="label"), html.div(settings["browser"], class_="value")], class_="summary-card"),
            html.div([html.div("Headless", class_="label"), html.div(str(settings["headless"]), class_="value")], class_="summary-card"),
            html.div([html.div("Timeout (s)", class_="label"), html.div(str(settings["wait_timeout"]), class_="value")], class_="summary-card"),
        ],
        class_="summary-grid",
    )
