# Scraper Service

Un microservicio FastAPI independiente que envuelve SeleniumBase para resolver el Cloudflare Turnstile de fbref.

## Ejecutar el servicio

```bash
# Instalar dependencias (solo para el servicio)
pip install -r requirements.txt

# Levantar el servicio (desde la raíz del proyecto)
python scraper_service/main.py
```

El servicio quedará escuchando en `http://localhost:5555`.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Verifica que el servicio esté activo |
| `POST` | `/scrape` | Devuelve el HTML de una URL tras pasar Cloudflare |

### Ejemplo de uso (curl)

```bash
curl -X POST http://localhost:5555/scrape \
     -H "Content-Type: application/json" \
     -d '{"url": "https://fbref.com/es/equipos/8602292d/Aston-Villa-Stats"}'
```

## Configuración

La URL del servicio se configura en el proyecto principal via la variable de entorno `SCRAPER_SERVICE_URL`.
Por defecto apunta a `http://localhost:5555`.

```bash
# Para apuntar a otro host (ej. en producción)
export SCRAPER_SERVICE_URL=http://mi-servidor-scraper:5555
```
