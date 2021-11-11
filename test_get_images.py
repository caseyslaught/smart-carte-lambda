
from datetime import datetime
import json

import intake_stac
import numpy as np

from app.sclib import helpers, utilities
#from app.sclib.utilities import cloud_mask, crop, filter_items_by_bands, get_bands, get_images, limit_items, stack




bbox1 = [29.2687, -1.5302, 29.3733, -1.3934] # southern sector
bbox2 = [-100.622848,31.313316,-100.530093,31.398142] # texas
bbox = bbox1

date = datetime.strptime('2021-10-05T20:06:58.943Z', '%Y-%m-%dT%H:%M:%S.%fZ')
items = utilities.get_images(bbox, date)
items.save('items.json')

catalog = intake_stac.catalog.StacItemCollection(items)
print(list(catalog))

item = catalog['S2B_35MQU_20210929_0_L2A']
print(item)

bands = utilities.get_bands("ndvi")
stack = item.stack_bands(bands)

darray = stack(chunks=dict(band=1, x=2048, y=2048)).to_dask()
darray = darray * 0.0001

darray.coords['scl'] = utilities.get_interpolated_scl(item, darray)
darray = darray.assign_attrs({'crs': item.metadata['proj:epsg']})
darray['band'] = bands
print('\n\ndarray\n', darray)

darray_clipped = utilities.clip(darray, bbox)
print('\n\ndarray_clipped\n', darray_clipped)

darray_masked = utilities.cloud_mask_s2(darray_clipped)
print('\n\ndarray_masked\n', darray_masked)

dset = darray_masked.to_dataset(dim='band')
print('\n\ndset\n', dset)

helpers.plot_image(dset['nir'])

exit(0)


subset = da.isel(x=slice(0, 1500), y=slice(7000, 8500)).compute()


not_cloudy = (subset.scl < 7) | (subset.scl == 11) 
no_clouds = subset.where(not_cloudy, other=0)
no_clouds['band'] = bands

ds = no_clouds.to_dataset(dim='band')

NDVI = (ds['nir'] - ds['red']) / (ds['nir'] + ds['red'])

helpers.plot_ndvi(NDVI) # looks like there are some weird outliers... much greater than 1

exit(0)


items = limit_items(items)
print(len(items), "items")


filtered_items = filter_items_by_bands(items, bands)
#print(filtered_items)

cropped_items = crop(filtered_items, bbox)
#print(cropped_items)

masked_items = [cloud_mask(item) for item in cropped_items]

stacked_items = [stack(item) for item in masked_items]
print(stacked_items[0]['stack'].shape)

for item in stacked_items:
    stack = item['stack']
    layers = item['layers']

    # not sure if masked values are being left out...
    # also need to check on plot min/max
    ndvi = (stack[:, :, layers['nir']] - stack[:, :, layers['red']]) / (stack[:, :, layers['nir']] + stack[:, :, layers['red']])
    print(ndvi.shape)
    print(ndvi)
    helpers.plot_image(ndvi)



# helpers.plot_image(cropped_items[0]['nir'])
# helpers.plot_image(masked_dict['nir'])


#href = filtered_items[0]['red']
#subset = utilities.test_crop(href, bbox)
#helpers.plot_href(href)




