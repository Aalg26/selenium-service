"""
Scraper Service — Microservicio de Scraping con SeleniumBase
============================================================
Ejecutar con:
    python scraper_service/main.py

O con uvicorn:
    uvicorn scraper_service.main:app --host 0.0.0.0 --port 5555
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
_request_count = 0
MAX_REQUESTS_BEFORE_RESTART = 50

def get_driver():
    """Inicializa o reutiliza el driver de Selenium con soporte para Docker y Proxy."""
    global _driver, _request_count

    if _driver is not None and _request_count >= MAX_REQUESTS_BEFORE_RESTART:
        logger.info(f"♻️ Límite de {MAX_REQUESTS_BEFORE_RESTART} peticiones alcanzado. Reiniciando Chrome para liberar RAM...")
        try:
            _driver.quit()
        except:
            pass
        _driver = None
        _request_count = 0

    if _driver is None:
        headless_env = os.getenv("HEADLESS", "true").lower()
        headless = headless_env in ("1", "true", "yes")
        

        logger.info(f"🚀 Iniciando Chrome indetectable... (headless={headless}, proxy={proxy_url})")

        safe_memory_flags = ",".join([
            "--disable-dev-shm-usage",
            "--no-sandbox",
            #"--disable-extensions",
        ])

        _driver = Driver(
            uc=True,
            headless2=headless,
            proxy=proxy_url,
            chromium_arg=safe_memory_flags
        )
        logger.info("✅ Navegador listo.")
        
    _request_count += 1
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
        
        if "Just a moment" in title or "Un momento" in title:
            logger.info("Cloudflare detectado. Intentando resolver captcha de forma interactiva...")
            try:
                driver.uc_gui_handle_cf()
                logger.info("Interacción con Cloudflare enviada.")
            except Exception as e:
                logger.warning(f"Advertencia al usar uc_gui_handle_cf: {e}")
                
            time.sleep(5)
            title = driver.title
            
            if "Just a moment" in title or "Un momento" in title:
                raise HTTPException(
                    status_code=403,
                    detail="Cloudflare Turnstile detectado en el título. El navegador no pudo resolverlo tras reitento."
                )

        html = driver.page_source

        logger.info(f"✅ Página obtenida correctamente: {driver.title}")
        
        try:
            driver.get("about:blank")
        except:
            pass
            
        return ScrapeResponse(html=html)

    except HTTPException:
        raise
    except Exception as e:

        global _driver, _request_count
        if _driver:
            try:
                _driver.quit()
            except:
                pass
        _driver = None
        _request_count = 0
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