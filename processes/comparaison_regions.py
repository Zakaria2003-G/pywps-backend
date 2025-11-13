from pywps import Process, LiteralInput, ComplexOutput, Format
import geopandas as gpd
import json

EQ_AREA_CRS = 26191  # EPSG:26191 (Maroc)

class Process(Process):
    def __init__(self):
        inputs = [
            LiteralInput("region_id_1", "Code de la première région", data_type="string"),
            LiteralInput("region_id_2", "Code de la deuxième région", data_type="string")
        ]
        outputs = [
            ComplexOutput("result", "Résultat JSON", supported_formats=[Format("application/json")])
        ]

        super().__init__(
            self._handler,
            identifier="comparaison_regions",
            title="Comparaison de deux régions",
            abstract="Compare deux régions du Maroc selon leur superficie, population et densité.",
            version="1.0",
            inputs=inputs,
            outputs=outputs
        )

    def _handler(self, request, response):
        id1 = request.inputs["region_id_1"][0].data
        id2 = request.inputs["region_id_2"][0].data

        # Charger le GeoJSON et corriger les noms de colonnes
        gdf = gpd.read_file("data/populationregion.geojson")
        gdf.columns = [c.strip() for c in gdf.columns]

        # Fonction interne de calcul
        def get_stats(region_id):
            sel = gdf[gdf["CODE_REGIO"].astype(str) == str(region_id)]
            if sel.empty:
                return None
            sel_proj = sel.to_crs(EQ_AREA_CRS)
            area_km2 = float(sel_proj.geometry.area.sum() / 1e6)
            pop = float(sel.iloc[0]["Populatio"])
            dens = round(pop / area_km2, 2) if area_km2 > 0 else None
            return {
                "code": region_id,
                "nom_region": sel.iloc[0]["nom_region"],
                "superficie_km2": round(area_km2, 2),
                "population": int(pop),
                "densite_hab_km2": dens
            }

        # Calculer pour les deux régions
        r1 = get_stats(id1)
        r2 = get_stats(id2)

        if not r1 or not r2:
            response.outputs["result"].data = json.dumps({
                "error": "Une ou les deux régions sont introuvables"
            }, ensure_ascii=False)
            return response

        # Comparaison directe
        comparaison = {
            "region_1": r1,
            "region_2": r2,
            "comparaison": {
                "plus_grande_superficie": r1["nom_region"] if r1["superficie_km2"] > r2["superficie_km2"] else r2["nom_region"],
                "plus_peuplee": r1["nom_region"] if r1["population"] > r2["population"] else r2["nom_region"],
                "plus_dense": r1["nom_region"] if r1["densite_hab_km2"] > r2["densite_hab_km2"] else r2["nom_region"]
            }
        }

        response.outputs["result"].data = json.dumps(comparaison, ensure_ascii=False, indent=2)
        return response
