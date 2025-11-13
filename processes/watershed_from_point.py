from pywps import Process, LiteralInput, ComplexOutput, Format
import whitebox
import geopandas as gpd
import json

class Process(Process):
    def __init__(self):
        inputs = [
            LiteralInput('x', 'Coordonnée X du point', data_type='float'),
            LiteralInput('y', 'Coordonnée Y du point', data_type='float')
        ]
        outputs = [
            ComplexOutput('result', 'Bassin versant (GeoJSON)',
                          supported_formats=[Format('application/json')])
        ]

        super().__init__(
            self._handler,
            identifier='watershed_from_point',
            title='Délimitation d’un bassin versant à partir d’un point',
            abstract='Délimite un bassin versant en utilisant un MNT et le flux hydrologique',
            version='1.0',
            inputs=inputs,
            outputs=outputs
        )

    def _handler(self, request, response):
        x = float(request.inputs['x'][0].data)
        y = float(request.inputs['y'][0].data)

        wbt = whitebox.WhiteboxTools()
        wbt.verbose = False
        wbt.work_dir = "data"

        dem = "data/mnt_maroc.tif"
        filled = "data/dem_filled.tif"
        flow_dir = "data/flow_dir.tif"
        output = "data/watershed.tif"

        # Pré-traitement
        wbt.fill_depressions(dem, filled)
        wbt.d8_pointer(filled, flow_dir)

        # Génération du bassin versant
        wbt.watershed(flow_dir, "data/point.shp", output)

        # Conversion en GeoJSON (facultatif)
        response.outputs['result'].data = json.dumps({
            "bassin": "data/watershed.tif",
            "status": "success"
        })
        return response
