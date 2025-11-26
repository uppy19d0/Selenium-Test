# Selenium Test Suite

## Instalación
- Clona el repositorio y abre una terminal en la raíz del proyecto.
- Crea y activa un entorno virtual:
  - macOS/Linux: `python -m venv .venv && source .venv/bin/activate`
  - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
- Instala dependencias: `pip install -r requirements.txt`
- Configura variables de entorno (o crea un `.env` a partir de `.env.example`):
  - `USERNAME` y `PASSWORD` para el login exitoso.
  - `FAIL_PASSWORD` para probar credenciales incorrectas.

## Configuración
- Ajusta `data/config.yaml` para elegir navegador (`chrome`/`firefox`), modo `headless` y `base_url`.
- El archivo `pytest.ini` ya deja configurado el reporte HTML en `results/report.html`.

## Ejecución de pruebas
- Ejecuta `pytest` desde la raíz del proyecto.
- El reporte HTML se genera en `results/report.html` con metadatos, descripciones y capturas automáticas en fallos.
