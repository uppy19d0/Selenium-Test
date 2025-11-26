import os
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pytest # type: ignore
from dotenv import load_dotenv # type: ignore
from py.xml import html  # type: ignore
from pytest_html import extras  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.service import Service as ServiceChrome # type: ignore
from selenium.webdriver.firefox.service import Service as ServiceFirefox # type: ignore
from selenium.webdriver.support.wait import WebDriverWait   # type: ignore
from webdriver_manager.chrome import ChromeDriverManager    # type: ignore
from webdriver_manager.firefox import GeckoDriverManager  # type: ignore

from utils.config import load_settings

RUN_STATS: Dict[str, object] = {
    "start": None,
    "end": None,
    "counts": {"passed": 0, "failed": 0, "skipped": 0, "error": 0},
    "duration": 0.0,
}

REPORT_INFO = {
    "title": "Prueba automatizada - Tarea 4 ITLA",
    "version": os.getenv("REPORT_VERSION", "1.0.0"),
    "team": os.getenv("REPORT_TEAM", "Pruebas Automatizadas ITLA"),
    "author": os.getenv("REPORT_AUTHOR", "Luis A. Tavarez"),
}

CUSTOM_CSS = """
* { box-sizing: border-box; }
body {font-family:'Segoe UI','Inter','Helvetica Neue',Arial,sans-serif; background:#f4f6fb; color:#1f2937; margin:0; padding:24px;}
a {color:#0ea5e9;}
.page {max-width:1200px; margin:0 auto;}
.header {background:#ffffff; border-radius:16px; padding:28px 30px; margin-bottom:22px; box-shadow:0 12px 32px rgba(0,0,0,0.08); border:1px solid #e5e7eb;}
.header h1 {color:#0f172a; font-size:2.2em; margin:0 0 8px; font-weight:800; letter-spacing:0.2px;}
.header .subtitle {color:#475569; font-size:1.05em; margin-bottom:16px;}
.meta-info {display:flex; justify-content:flex-start; flex-wrap:wrap; gap:12px; margin-top:12px;}
.meta-item {background:#f8fafc; padding:12px 16px; border-radius:12px; border:1px solid #e2e8f0;}
.meta-item strong {color:#0f172a; display:block; font-size:0.85em; margin-bottom:4px; letter-spacing:0.3px;}
.meta-item span {color:#1f2937; font-size:1em; font-weight:700;}
.container {background:#ffffff; border-radius:16px; padding:24px 26px; box-shadow:0 12px 32px rgba(0,0,0,0.08); margin-bottom:22px; border:1px solid #e5e7eb;}
.exec-summary {background:linear-gradient(135deg,#0ea5e920,#0ea5e910); border:1px solid #bae6fd; border-left:6px solid #0ea5e9; padding:20px; border-radius:12px; margin-bottom:20px;}
.exec-summary h2 {color:#0f172a; margin:0 0 10px; font-size:1.2em;}
.exec-summary p, .exec-summary ul {color:#334155; line-height:1.6;}
.exec-summary ul {padding-left:18px; margin:8px 0 12px;}
.badge {display:inline-block; padding:6px 12px; border-radius:14px; color:#0f172a; font-weight:700; margin-right:8px; border:1px solid #e2e8f0; background:#f8fafc;}
.badge.pass {border-color:#22c55e; color:#14532d; background:#dcfce7;}
.badge.fail {border-color:#f97316; color:#7c2d12; background:#ffedd5;}
.badge.skip {border-color:#eab308; color:#854d0e; background:#fef9c3;}
.stats-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; margin:16px 0;}
.stat-card {background:linear-gradient(135deg,#1d4ed8,#0ea5e9); color:#fff; padding:18px; border-radius:12px; text-align:left; box-shadow:0 10px 26px rgba(0,0,0,0.12); transition:transform 0.2s ease;}
.stat-card:hover {transform:translateY(-3px);}
.stat-number {font-size:1.9em; font-weight:800; margin-bottom:4px;}
.stat-label {font-size:0.95em; opacity:0.9;}
.passed {background:linear-gradient(135deg,#16a34a,#22c55e);}
.failed {background:linear-gradient(135deg,#e11d48,#f97316);}
.skipped {background:linear-gradient(135deg,#ca8a04,#facc15);}
.error {background:linear-gradient(135deg,#8b5cf6,#6366f1);}
.progress-container {margin:18px 0;}
.progress-bar {width:100%; height:16px; background:#e2e8f0; border-radius:10px; overflow:hidden; box-shadow:inset 0 2px 4px rgba(0,0,0,0.08);}
.progress-fill {height:100%; background:linear-gradient(90deg,#22c55e,#0ea5e9); transition:width 0.6s ease; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:700; font-size:0.85em;}
.cards-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; margin:12px 0 8px;}
.card {background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 16px; box-shadow:0 8px 20px rgba(0,0,0,0.05);}
.card h4 {margin:0 0 6px; color:#0f172a; font-size:1em;}
.card p {margin:2px 0; color:#334155; font-size:0.95em; line-height:1.5;}
.table-wrap {width:100%; overflow-x:auto;}
#results-table {width:100%; border-collapse:collapse; margin:16px 0; border-radius:12px; overflow:hidden; box-shadow:0 8px 22px rgba(0,0,0,0.08);}
#results-table th {background:#0f172a; color:#fff; padding:14px; text-align:left; font-weight:700; letter-spacing:0.2px;}
#results-table td {padding:12px 14px; border-bottom:1px solid #e2e8f0;}
#results-table tr:nth-child(even) td {background:#f8fafc;}
#results-table tr:hover td {background:#e0f2fe;}
.status-badge {padding:6px 12px; border-radius:18px; font-size:0.85em; font-weight:800; text-transform:uppercase; letter-spacing:0.3px;}
.status-badge.passed {background:#dcfce7; color:#166534;}
.status-badge.failed {background:#fee2e2; color:#991b1b;}
.status-badge.error {background:#ffe4e6; color:#9f1239;}
.status-badge.skipped {background:#fef9c3; color:#854d0e;}
.col-description {max-width:420px;}
.case-id {font-weight:800; color:#0f172a;}
.case-node {color:#64748b; font-size:12px;}
.evidence {display:flex; gap:8px; flex-wrap:wrap;}
.evidence-item {background:#f8fafc; border-radius:12px; padding:8px; display:flex; align-items:center; gap:8px; border:1px solid #e2e8f0;}
.evidence-item img {height:72px; width:auto; border-radius:10px; border:1px solid #e2e8f0; object-fit:cover;}
.evidence-label {font-size:12px; color:#0f172a; font-weight:600;}
.evidence-link {display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:14px; background:#e2e8f0; color:#0f172a; font-size:0.85em; text-decoration:none; font-weight:700;}
.evidence-link:hover {background:#cbd5e1;}
.lightbox {position:fixed; inset:0; background:rgba(0,0,0,0.75); display:none; align-items:center; justify-content:center; z-index:9999; padding:40px 20px;}
.lightbox.open {display:flex;}
.lightbox-content {max-width:90%; max-height:90%; background:#0f172a; border-radius:12px; overflow:hidden; box-shadow:0 20px 45px rgba(0,0,0,0.45); display:flex; flex-direction:column;}
.lightbox img {max-width:100%; max-height:70vh; object-fit:contain; background:#000;}
.lightbox-footer {padding:16px 20px; color:#e2e8f0; display:flex; justify-content:space-between; align-items:center; gap:16px; flex-wrap:wrap;}
.lightbox-footer span {font-size:0.95em;}
.close-modal {background:#ef4444; border:none; color:#fff; padding:8px 16px; border-radius:6px; cursor:pointer; font-weight:700;}
.footer {background:#fff; border-radius:12px; padding:16px; text-align:center; color:#64748b; box-shadow:0 5px 15px rgba(0,0,0,0.08); margin-top:18px; border:1px solid #e5e7eb;}
@media (max-width: 720px) {
  body {padding:16px;}
  .header, .container {padding:18px;}
  #results-table th, #results-table td {padding:10px;}
  .meta-info {flex-direction:column; align-items:flex-start;}
  .stat-card {text-align:center;}
  .lightbox-content {max-width:100%; max-height:100%;}
}
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
            "Reporte": REPORT_INFO["title"],
            "Versión": REPORT_INFO["version"],
            "Equipo": REPORT_INFO["team"],
            "Autor": REPORT_INFO["author"],
            "Report generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    config._metadata = metadata

    reports_dir = Path("results")
    reports_dir.mkdir(exist_ok=True)


def pytest_html_report_title(report):
    report.title = REPORT_INFO["title"]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach description and screenshots to the HTML report."""
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__ or "Sin descripción").strip()
    report.case_id = _case_identifier(item)

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

    screenshot_base64 = driver.get_screenshot_as_base64()
    if report.failed:
        extra.append(extras.image(screenshot_base64, "base64", "Captura al fallar"))
        if current_url:
            extra.append(extras.url(current_url, name="URL al fallar"))
            extra.append(extras.text(f"Título: {driver.title}", name="Página"))
    else:
        extra.append(extras.image(screenshot_base64, "base64", "Captura final"))

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
    cells[2] = html.td(_case_cell(report), class_="col-name")
    cells.append(html.td(_evidence_cell(report), class_="col-evidence"))


def pytest_html_results_summary(prefix, summary, postfix):
    """Add a compact resumen de entorno al inicio del reporte."""
    settings = load_settings()
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metrics = _compute_metrics()
    hero = html.div(
        [
            html.h1(f"🧪 {REPORT_INFO['title']}", class_="report-title"),
            html.p("Pruebas automatizadas - Tarea 4 ITLA", class_="report-subtitle"),
            html.div(
                [
                    html.span(f"Versión: {REPORT_INFO['version']}", class_="meta-chip"),
                    html.span(f"Fecha: {generated.split(' ')[0]}", class_="meta-chip"),
                    html.span(f"Hora: {generated.split(' ')[1]}", class_="meta-chip"),
                    html.span(f"Equipo: {REPORT_INFO['team']}", class_="meta-chip"),
                    html.span(f"Autor: {REPORT_INFO['author']}", class_="meta-chip"),
                    html.span(f"Base URL: {settings['base_url']}", class_="meta-chip"),
                ],
                class_="report-meta",
            ),
        ],
        class_="report-header",
    )
    exec_summary = _build_exec_summary(metrics)
    stats_grid = _build_stats_cards(metrics)
    progress = _build_progress(metrics)
    meta_cards = _build_meta_cards(settings, metrics, generated)
    content = [
        html.style(CUSTOM_CSS),
        hero,
        meta_cards,
        exec_summary,
        stats_grid,
        progress,
        _build_env_cards(settings),
    ]
    prefix[0:0] = [html.div(content, class_="page")]
    summary.clear()
    postfix.extend(_build_lightbox())
    postfix.append(_build_table_wrapper_script())
    postfix.append(_build_footer())


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
                    [
                        html.a(image, href=content, target="_blank", **{"data-evidence": content, "data-label": name, "class": "evidence-link"}),
                        html.span(name, class_="evidence-label"),
                    ],
                    class_="evidence-item image",
                )
            )
        elif extra_format == "url" and content:
            items.append(
                html.div(
                    [
                        html.span("Link", class_="evidence-label"),
                        html.a(name, href=content, target="_blank", class_="evidence-link", **{"data-evidence": content, "data-label": name}),
                    ],
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
    metrics = _compute_metrics()
    cards = [
        html.div([html.div("Pruebas Exitosas", class_="stat-label"), html.div(str(metrics["passed"]), class_="stat-number")], class_="stat-card passed"),
        html.div([html.div("Pruebas Fallidas", class_="stat-label"), html.div(str(metrics["failed"]), class_="stat-number")], class_="stat-card failed"),
        html.div([html.div("Pruebas Omitidas", class_="stat-label"), html.div(str(metrics["skipped"]), class_="stat-number")], class_="stat-card skipped"),
        html.div([html.div("Errores", class_="stat-label"), html.div(str(metrics["error"]), class_="stat-number")], class_="stat-card error"),
        html.div([html.div("Tasa de Éxito", class_="stat-label"), html.div(f"{metrics['pass_rate']:.1f}%", class_="stat-number")], class_="stat-card"),
    ]
    return html.div(cards, class_="stats-grid")


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


def _build_meta_cards(settings, metrics, generated):
    cards = [
        html.div(
            [
                html.h4("Contexto"),
                html.p(f"Equipo: {REPORT_INFO['team']}"),
                html.p(f"Autor: {REPORT_INFO['author']}"),
                html.p(f"Fecha: {generated.split(' ')[0]} {generated.split(' ')[1]}"),
            ],
            class_="card",
        ),
        html.div(
            [
                html.h4("Resultados"),
                html.p(f"Total: {metrics['total']}"),
                html.p(f"Aprobadas: {metrics['passed']} | Fallidas: {metrics['failed']} | Omitidas: {metrics['skipped']}"),
                html.p(f"Tasa de éxito: {metrics['pass_rate']:.1f}%"),
            ],
            class_="card",
        ),
        html.div(
            [
                html.h4("Ejecución"),
                html.p(f"Navegador: {settings['browser']} | Headless: {settings['headless']}"),
                html.p(f"Timeout espera: {settings['wait_timeout']}s"),
                html.p(f"Duración total: {metrics['duration']:.2f}s"),
            ],
            class_="card",
        ),
    ]
    return html.div(cards, class_="cards-grid")


def _build_exec_summary(metrics: Dict[str, float]):
    total = metrics["total"]
    pass_rate = metrics["pass_rate"]
    duration = metrics["duration"]
    return html.div(
        [
            html.h2("📊 Resumen Ejecutivo"),
            html.p(
                f"Se ejecutaron {total} pruebas con una tasa de éxito de {pass_rate:.1f}%. "
                f"El tiempo total de ejecución fue de {duration:.2f} segundos."
            ),
            html.ul(
                [
                    html.li(f"✅ {metrics['passed']} pruebas exitosas."),
                    html.li(f"❌ {metrics['failed']} fallidas."),
                    html.li(f"⏭️ {metrics['skipped']} omitidas."),
                ]
            ),
            html.div(
                [
                    html.span(f"✅ {metrics['passed']} Exitosas", class_="badge pass"),
                    html.span(f"❌ {metrics['failed']} Fallidas", class_="badge fail"),
                    html.span(f"⏭️ {metrics['skipped']} Omitidas", class_="badge skip"),
                ]
            ),
        ],
        class_="exec-summary",
    )


def _build_stats_cards(metrics: Dict[str, float]):
    return html.div(
        [
            html.div([html.div(str(metrics["passed"]), class_="stat-number"), html.div("Pruebas Exitosas", class_="stat-label")], class_="stat-card passed"),
            html.div([html.div(str(metrics["failed"]), class_="stat-number"), html.div("Pruebas Fallidas", class_="stat-label")], class_="stat-card failed"),
            html.div([html.div(str(metrics["skipped"]), class_="stat-number"), html.div("Pruebas Omitidas", class_="stat-label")], class_="stat-card skipped"),
            html.div([html.div(f"{metrics['pass_rate']:.1f}%", class_="stat-number"), html.div("Tasa de Éxito", class_="stat-label")], class_="stat-card"),
        ],
        class_="stats-grid",
    )


def _build_progress(metrics: Dict[str, float]):
    return html.div(
        [
            html.h3("🎯 Progreso General"),
            html.div(
                html.div(f"{metrics['pass_rate']:.1f}%", class_="progress-fill", **{"data-width": f"{metrics['pass_rate']:.1f}%"}),
                class_="progress-bar",
            ),
        ],
        class_="progress-container container",
    )


def _case_identifier(item):
    marker = item.get_closest_marker("case_id")
    if marker and marker.args:
        return str(marker.args[0])
    return item.name.replace("test_", "").replace("_", " ").title()


def _case_cell(report):
    case_id = getattr(report, "case_id", report.nodeid)
    node = getattr(report, "nodeid", "")
    return html.div(
        [
            html.div(case_id, class_="case-id"),
            html.div(node, class_="case-node"),
        ]
    )


def _compute_metrics() -> Dict[str, float]:
    counts = RUN_STATS["counts"]
    total = sum(counts.values()) or 0
    duration = float(RUN_STATS.get("duration", 0.0))
    wall_clock = None
    if RUN_STATS.get("start") and RUN_STATS.get("end"):
        wall_clock = (RUN_STATS["end"] - RUN_STATS["start"]).total_seconds()
    pass_rate = (counts.get("passed", 0) / total * 100) if total else 0.0
    return {
        "passed": counts.get("passed", 0),
        "failed": counts.get("failed", 0),
        "skipped": counts.get("skipped", 0),
        "error": counts.get("error", 0),
        "total": total,
        "duration": duration,
        "wall_clock": wall_clock,
        "pass_rate": pass_rate,
    }


def _build_lightbox():
    script = """
    document.addEventListener('DOMContentLoaded', function() {
        const progressBar = document.querySelector('.progress-fill');
        if (progressBar) {
            setTimeout(() => {
                progressBar.style.width = progressBar.dataset.width || '0%';
            }, 200);
        }
        const modal = document.querySelector('#evidence-modal');
        const modalImage = modal ? modal.querySelector('img') : null;
        const modalCaption = modal ? modal.querySelector('.modal-caption') : null;
        const closeButton = modal ? modal.querySelector('.close-modal') : null;
        const openModal = (src, label) => {
            if (!modal || !modalImage) return;
            modalImage.src = src;
            modalImage.alt = label || 'Evidencia';
            if (modalCaption) modalCaption.textContent = label || 'Evidencia';
            modal.classList.add('open');
            document.body.classList.add('lightbox-open');
        };
        const closeModal = () => {
            if (!modal) return;
            modal.classList.remove('open');
            document.body.classList.remove('lightbox-open');
            if (modalImage) modalImage.src = '';
        };
        document.querySelectorAll('[data-evidence]').forEach(link => {
            link.addEventListener('click', event => {
                event.preventDefault();
                const imagePath = link.getAttribute('data-evidence');
                if (!imagePath) return;
                const label = link.getAttribute('data-label') || 'Evidencia';
                openModal(imagePath, label);
            });
        });
        if (modal) {
            modal.addEventListener('click', event => {
                if (event.target === modal) closeModal();
            });
        }
        if (closeButton) {
            closeButton.addEventListener('click', closeModal);
        }
        document.addEventListener('keydown', event => {
            if (event.key === 'Escape') closeModal();
        });
    });
    """
    lightbox_markup = html.div(
        html.div(
            [
                html.img(src="", alt="Evidencia de prueba", loading="lazy"),
                html.div(
                    [
                        html.span("Evidencia de prueba", class_="modal-caption"),
                        html.button("Cerrar", type="button", class_="close-modal"),
                    ],
                    class_="lightbox-footer",
                ),
            ],
            class_="lightbox-content",
        ),
        id="evidence-modal",
        **{"class": "lightbox", "aria-hidden": "true"},
    )
    return [lightbox_markup, html.script(script)]


def _build_table_wrapper_script():
    script = """
    document.addEventListener('DOMContentLoaded', function() {
        if (!document.querySelector("meta[name='viewport']")) {
            const meta = document.createElement('meta');
            meta.name = 'viewport';
            meta.content = 'width=device-width, initial-scale=1';
            document.head.appendChild(meta);
        }
        const table = document.querySelector('#results-table');
        if (table && !table.parentElement.classList.contains('table-wrap')) {
            const wrap = document.createElement('div');
            wrap.className = 'table-wrap';
            table.parentNode.insertBefore(wrap, table);
            wrap.appendChild(table);
        }
    });
    """
    return html.script(script)


def _build_footer():
    return html.div(f"© {datetime.now().year} {REPORT_INFO['team']} | {REPORT_INFO['title']}", class_="footer")
