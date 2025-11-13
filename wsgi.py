from pywps.app.Service import Service
from processes import population_stats, region_area, area_agri, comparaison_regions, era5_mean

# --- Liste des processus disponibles ---
processes = [
    population_stats.Process(),
    region_area.Process(),
    area_agri.Process(),
    comparaison_regions.Process(),
    era5_mean.Process(),
]

wps_app = Service(processes)

# =====================================================
#  Middleware CORS compatible Render / Railway / Browser
# =====================================================

def application(environ, start_response):
    def cors_start_response(status, headers, exc_info=None):
        headers.append(("Access-Control-Allow-Origin", "*"))
        headers.append(("Access-Control-Allow-Methods", "GET, POST, OPTIONS"))
        headers.append(("Access-Control-Allow-Headers", "Content-Type"))
        return start_response(status, headers, exc_info)

    # Acceptation automatique des requêtes préflight (OPTIONS)
    if environ["REQUEST_METHOD"] == "OPTIONS":
        cors_start_response("200 OK", [("Content-Type", "text/plain")])
        return [b""]

    return wps_app(environ, cors_start_response)
