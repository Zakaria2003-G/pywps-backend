from pywps import Process, LiteralInput, ComplexOutput, Format
import xarray as xr
import geopandas as gpd
import json

class Process(Process):
    def __init__(self):
        inputs = [
            LiteralInput('region_id', 'ID de la région', data_type='string'),
            LiteralInput('variable', 'Nom de la variable ERA5', data_type='string'),
            LiteralInput('start_date', 'Date de début', data_type='string'),
            LiteralInput('end_date', 'Date de fin', data_type='string')
        ]
        outputs = [
            ComplexOutput('result', 'Résultat JSON',
                          supported_formats=[Format('application/json')])
        ]

        super().__init__(
            self._handler,
            identifier='era5_mean',
            title='Moyenne ERA5 sur une région donnée',
            abstract='Calcule la moyenne ERA5 sur une période et une région définie',
            version='1.0',
            inputs=inputs,
            outputs=outputs
        )

    def _handler(self, request, response):
        region_id = request.inputs['region_id'][0].data
        variable = request.inputs['variable'][0].data
        start_date = request.inputs['start_date'][0].data
        end_date = request.inputs['end_date'][0].data

        # Lecture des données ERA5
        ds = xr.open_dataset('data/era5.nc')
        subset = ds[variable].sel(time=slice(start_date, end_date))
        mean_val = float(subset.mean().values)

        response.outputs['result'].data = json.dumps({
            "region": region_id,
            "variable": variable,
            "mean_value": round(mean_val, 3)
        })
        return response
