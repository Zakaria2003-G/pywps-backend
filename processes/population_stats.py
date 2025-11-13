from pywps import Process, LiteralInput, ComplexOutput, Format
import geopandas as gpd
import json

class Process(Process):
    def __init__(self):
        # Définition des entrées et sorties du processus
        inputs = [
            LiteralInput("top_n", "Nombre de régions à afficher (1–12)",
                         data_type="integer", min_occurs=0, max_occurs=1)
        ]

        outputs = [
            ComplexOutput("result", "Résultat JSON",
                          supported_formats=[Format("application/json")])
        ]

        super().__init__(
            self._handler,
            identifier="population_stats",
            title="Statistiques régionales",
            abstract="Top-N régions selon la population totale + statistiques globales.",
            version="1.0",
            inputs=inputs,
            outputs=outputs
        )

    def _handler(self, request, response):
        # Lecture du paramètre d'entrée (par défaut = 5)
        top_n = int(request.inputs["top_n"][0].data) if "top_n" in request.inputs else 5

        # Lecture du GeoJSON contenant les régions
        gdf = gpd.read_file("data/populationregion.geojson")

        # 🧹 Nettoyage des noms de colonnes (supprime les espaces)
        gdf.rename(columns=lambda c: c.strip(), inplace=True)

        # Conversion du champ de population en float
        if "Populatio" not in gdf.columns:
            response.outputs["result"].data = json.dumps({"error": "Champ 'Populatio' non trouvé dans le GeoJSON"})
            return response

        gdf["Populatio"] = gdf["Populatio"].astype(float)

        # Calculs statistiques
        total = gdf["Populatio"].sum()
        mean = gdf["Populatio"].mean()
        maxi = gdf["Populatio"].max()
        mini = gdf["Populatio"].min()

        # Classement des régions
        top = gdf.sort_values("Populatio", ascending=False).head(top_n)

        # Construction du résultat JSON
        result = {
            "regions_totales": int(len(gdf)),
            "population_totale": int(total),
            "population_moyenne": round(mean, 2),
            "max_population": int(maxi),
            "min_population": int(mini),
            "top_regions": [
                {
                    "code": str(row["CODE_REGIO"]),
                    "nom": row["nom_region"],
                    "population": int(row["Populatio"])
                }
                for _, row in top.iterrows()
            ]
        }

        # Envoi du résultat
        response.outputs["result"].data = json.dumps(result, ensure_ascii=False)
        return response
