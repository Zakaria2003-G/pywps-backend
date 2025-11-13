from pywps import Process, LiteralInput, ComplexOutput, Format
import geopandas as gpd
import json
import rioxarray as rxr

class Process(Process):
    def __init__(self):
        inputs = [
            LiteralInput('region_id', 'ID de la région', data_type='string')
        ]
        outputs = [
            ComplexOutput('result', 'Résultat JSON',
                          supported_formats=[Format('application/json')])
        ]

        super().__init__(
            self._handler,
            identifier='area_agri',
            title='Superficie agricole par région',
            abstract='Calcule la superficie agricole en intersectant une couche régionale et un raster d’occupation du sol',
            version='1.0',
            inputs=inputs,
            outputs=outputs
        )

    def _handler(self, request, response):
        # Récupération de l’ID de la région
        region_id = request.inputs['region_id'][0].data

        # Lecture du fichier GeoPackage des régions
        regions = gpd.read_file('data/regions.gpkg').to_crs(26191)
        region = regions[regions['REG_ID'] == region_id]

        # Lecture du raster (WorldCover)
        lc = rxr.open_rasterio('data/worldcover_10m.tif').squeeze()
        lc_clip = lc.rio.clip(region.geometry, region.crs, drop=True)

        # Masque des classes agricoles
        mask = lc_clip.isin([40, 50])
        pixel_count = int(mask.sum())
        res = abs(lc.rio.resolution()[0])
        area_ha = pixel_count * (res ** 2) / 10000.0

        response.outputs['result'].data = json.dumps({
            'region': region_id,
            'superficie_agricole_ha': round(area_ha, 2)
        })
        return response
