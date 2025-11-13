from pywps import Process, LiteralInput, ComplexOutput, Format
import geopandas as gpd
import json

EQ_AREA_CRS = 26191  # EPSG:26191 (Maroc)

class Process(Process):
    def __init__(self):
        inputs = [
            LiteralInput("region_id", "Code de la région", data_type="string")
        ]
        outputs = [
            ComplexOutput("result", "Résultat JSON", supported_formats=[Format("application/json")])
        ]
        super().__init__(
            self._handler,
            identifier="region_area",
            title="Superficie et densité de population",
            abstract="Calcule la superficie (km²) et la densité de population d'une région donnée à partir du GeoJSON.",
            version="1.0",
            inputs=inputs,
            outputs=outputs
        )

    def _handler(self, request, response):
        rid = request.inputs["region_id"][0].data

        # Lecture du GeoJSON
        gdf = gpd.read_file("data/populationregion.geojson")

        # Nettoyage des noms de colonnes (supprime espaces)
        gdf.columns = [c.strip() for c in gdf.columns]

        # Filtrage
        sel = gdf[gdf["CODE_REGIO"].astype(str) == str(rid)]
        if sel.empty:
            response.outputs["result"].data = json.dumps({"error": f"Région {rid} introuvable"})
            return response

        # Calcul de superficie (en km²)
        sel_proj = sel.to_crs(EQ_AREA_CRS)
        area_km2 = float(sel_proj.geometry.area.sum() / 1e6)

        # Population totale
        pop = float(sel.iloc[0]["Populatio"])
        density = round(pop / area_km2, 2) if area_km2 > 0 else None

        result = {
            "code_region": rid,
            "nom_region": sel.iloc[0]["nom_region"],
            "superficie_km2": round(area_km2, 2),
            "population_totale": int(pop),
            "densite_hab_km2": density
        }

        response.outputs["result"].data = json.dumps(result, ensure_ascii=False)
        return response
