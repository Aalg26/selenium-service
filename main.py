"""
Scraper Service — Microservicio de Scraping con SeleniumBase
============================================================
Ejecutar con:
    python scraper_service/main.py

O con uvicorn:
    uvicorn scraper_service.main:app --host 0.0.0.0 --port 5555

El servicio mantiene una sesión de Chrome abierta entre peticiones
para mayor velocidad y consistencia de cookies/sesión con fbref.
"""
import time
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from seleniumbase import Driver
import logging

app = FastAPI(
    title="Scraper Service",
    description="Microservicio independiente que usa SeleniumBase para bypassear Cloudflare Turnstile.",
    version="1.0.0"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Driver global reutilizado entre peticiones para evitar abrir Chrome en cada request
_driver = None

def get_driver():
    """Inicializa o reutiliza el driver de Selenium."""
    global _driver
    if _driver is None:
        # Leer configuración desde variables de entorno para entornos cloud
        headless_env = os.getenv("HEADLESS", "true").lower()
        headless = headless_env in ("1", "true", "yes")

        logger.info("🚀 Iniciando navegador Chrome indetectable... (headless=%s)" % headless)
        _driver = Driver(uc=True,headless2=headless
)
        logger.info("✅ Navegador listo.")
    return _driver


class ScrapeRequest(BaseModel):
    url: str


class ScrapeResponse(BaseModel):
    html: str
    status: str = "ok"


@app.get("/health")
def health_check():
    """Endpoint para verificar que el servicio está activo."""
    return {"status": "running", "browser_active": _driver is not None}


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_url(request: ScrapeRequest):
    """
    Recibe una URL y devuelve el HTML de la página tras pasar Cloudflare.
    Mantiene la misma sesión de Chrome entre peticiones.
    """
    try:
        driver = get_driver()
        logger.info(f"🌐 Navegando a {request.url}")
        driver.uc_open_with_reconnect(request.url, 4)
        time.sleep(5)
        title = driver.title
        logger.info(f"Título de la página: {title}")
        if "Just a moment" in title or "Un momento"  in title:
            raise HTTPException(
                status_code=403,
                detail="Cloudflare Turnstile detectado. El navegador no pudo resolverlo."
            )

        html = driver.page_source

        # Verificación: detectar si Cloudflare bloqueó
        if "Just a moment" in html or 'id="challenge-running"' in html:
            raise HTTPException(
                status_code=403,
                detail="Cloudflare Turnstile detectado. El navegador no pudo resolverlo."
            )

        logger.info(f"✅ Página obtenida correctamente: {driver.title}")
        return ScrapeResponse(html=html)

    except HTTPException:
        raise
    except Exception as e:
        # Si el driver murió, limpiamos para que se reinicie en la próxima petición
        global _driver
        _driver = None
        raise HTTPException(status_code=500, detail=f"Error interno del scraper: {str(e)}")


@app.on_event("shutdown")
def shutdown_event():
    """Cierra el navegador al apagar el servicio."""
    global _driver
    if _driver:
        logger.info("🛑 Cerrando navegador...")
        _driver.quit()
        _driver = None


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5555))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)

