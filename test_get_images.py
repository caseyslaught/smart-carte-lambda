
from datetime import datetime
import json

import intake_stac
import numpy as np
import xarray as xr

from app.sclib import helpers, utilities


bbox1 = [29.2687, -1.5302, 29.3733, -1.3934] # southern sector
bbox2 = [-100.622848,31.313316,-100.530093,31.398142] # texas
bbox = bbox1

index = 'ndvi'
bands = utilities.get_bands(index)


start_date = datetime.strptime('2020-10-05T20:06:58.943Z', '%Y-%m-%dT%H:%M:%S.%fZ')
start_items = utilities.get_images(bbox, start_date)
start_catalog = intake_stac.catalog.StacItemCollection(start_items)
print(list(start_catalog))
start_darray_composite = utilities.get_composite_darray(start_catalog, bands, bbox)
#print('\n\ndarray_composite\n', darray_composite)
start_ds = start_darray_composite.to_dataset(dim='band')
start_ndvi = (start_ds['nir'] - start_ds['red']) / (start_ds['nir'] + start_ds['red'])
start_ndvi_path = 'C:/Users/casey/Desktop/ndvi_start.png'
helpers.save_ndvi(start_ndvi, start_ndvi_path)

end_date = datetime.strptime('2021-10-05T20:06:58.943Z', '%Y-%m-%dT%H:%M:%S.%fZ')
end_items = utilities.get_images(bbox, end_date)
end_catalog = intake_stac.catalog.StacItemCollection(end_items)
print(list(end_catalog))
end_darray_composite = utilities.get_composite_darray(end_catalog, bands, bbox)
#print('\n\ndarray_composite\n', darray_composite)
end_ds = end_darray_composite.to_dataset(dim='band')
end_ndvi = (end_ds['nir'] - end_ds['red']) / (end_ds['nir'] + end_ds['red'])
end_ndvi_path = 'C:/Users/casey/Desktop/ndvi_end.png'
helpers.save_ndvi(end_ndvi, end_ndvi_path)

# TODO: this looks a bit weird...
ndvi_diff = end_ndvi - start_ndvi
print(ndvi_diff)
helpers.plot_histogram(ndvi_diff)

end_ndvi_path = 'C:/Users/casey/Desktop/ndvi_diff.png'
helpers.save_image(ndvi_diff, end_ndvi_path)
