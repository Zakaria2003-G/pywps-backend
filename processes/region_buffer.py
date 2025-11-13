from pywps import Process, LiteralInput, ComplexOutput, Format
import geopandas as gpd

EQ_AREA_CRS = 26191  # EPSG:26191 (Maroc)

class Process(Process):
    def __init__(self):
        inputs = [
            LiteralInput("region_id", "Code de la région", data_type="string"),
            LiteralInput("distance_km", "Distance du buffer (km)", data_type="float")
        ]
        outputs = [
            ComplexOutput("buffer_geojson", "Tampon GeoJSON", supported_formats=[Format("application/json")])
        ]
        super().__init__(
            self._handler,
            identifier="region_buffer",
            title="Tampon autour d’une région",
            abstract="Crée un buffer autour d’une région donnée à partir du GeoJSON.",
            version="1.0",
            inputs=inputs,
            outputs=outputs
        )

    def _handler(self, request, response):
        rid = request.inputs["region_id"][0].data
        dist_km = float(request.inputs["distance_km"][0].data)

        # Charger et nettoyer le GeoJSON
        gdf = gpd.read_file("data/populationregion.geojson")
        gdf.columns = [c.strip() for c in gdf.columns]

        sel = gdf[gdf["CODE_REGIO"].astype(str) == str(rid)]
        if sel.empty:
            response.outputs["buffer_geojson"].data = '{"error":"Région introuvable"}'
            return response

        sel_eq = sel.to_crs(EQ_AREA_CRS)
        buf = sel_eq.buffer(dist_km * 1000)

        out = gpd.GeoDataFrame(
            sel[["CODE_REGIO", "nom_region"]],
            geometry=buf,
            crs=EQ_AREA_CRS
        ).to_crs(4326)

        response.outputs["buffer_geojson"].data = out.to_json()
        return response
