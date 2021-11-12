
from datetime import datetime
import json

import intake_stac
import numpy as np
import xarray as xr

from app.sclib import helpers, utilities


bbox1 = [29.2687, -1.5302, 29.3733, -1.3934] # southern sector
bbox2 = [-100.622848,31.313316,-100.530093,31.398142] # texas
bbox = bbox1

bands = utilities.get_bands("ndvi")

date = datetime.strptime('2020-10-05T20:06:58.943Z', '%Y-%m-%dT%H:%M:%S.%fZ')
items = utilities.get_images(bbox, date)

catalog = intake_stac.catalog.StacItemCollection(items)
print(list(catalog))

darray_composite = utilities.get_composite_darray(catalog, bands, bbox)
print('\n\ndarray_composite\n', darray_composite)

ds = darray_composite.to_dataset(dim='band')
ndvi = (ds['nir'] - ds['red']) / (ds['nir'] + ds['red'])
ndvi_path = 'C:/Users/casey/Desktop/ndvi.png'
helpers.save_ndvi(ndvi, ndvi_path)

exit()



