
from datetime import datetime, timedelta

import numpy as np
from pyproj import Proj, transform
from satsearch import Search
import xarray as xr

from app.sclib import indices, helpers


def clip(darray, bbox):

    p1 = Proj(init='epsg:4326')
    p2 = Proj(init=f'epsg:{darray.attrs["crs"]}')

    min_lon, max_lat = transform(p1, p2, bbox[0], bbox[3])
    max_lon, min_lat = transform(p1, p2, bbox[2], bbox[1])

    mask_lon = (darray.x >= min_lon) & (darray.x <= max_lon)
    mask_lat = (darray.y >= min_lat) & (darray.y <= max_lat)

    return darray.where(mask_lon & mask_lat, drop=True)


def cloud_mask_s2(darray):
    # 3: cloud shadows; 8: medium cloud; 9: high cloud
    mask = np.logical_not(darray.scl.isin([3, 8, 9]))
    return darray.where(mask, drop=True)


def get_bands(index):
    return indices.INDICES.get(index, indices.INDICES['ndvi'])


def get_images(bbox, target_date):
    
    start = target_date - timedelta(days=30)
    end = target_date + timedelta(days=30)
    date_range = start.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end.strftime('%Y-%m-%dT%H:%M:%SZ')

    search = Search(bbox=bbox, 
                    url='https://earth-search.aws.element84.com/v0',
                    datetime=date_range, 
                    query={'eo:cloud_cover': {'lt': 30}}, 
                    collections=['sentinel-s2-l2a-cogs'],
                    sort=[{"field": "datetime", "direction": "desc"}])

    items = search.items() # limit does not work
    return items 


def get_interpolated_scl(item, darray):

    da_scl = item.SCL.to_dask()
    da_scl = da_scl.interp(y=darray['y'], x=darray['x'],
                            kwargs={'fill_value':'extrapolate'},
                            method='nearest').squeeze('band', drop=True)

    return da_scl.compute().astype('uint8')



def get_composite_darray(catalog, bands, bbox):
    darray_list = list()
    for id in catalog:
        item = catalog[id]
        darray_list.append(preprocess_item(item, bands, bbox))

    darray_catalog = xr.concat(darray_list, 'datetime')
    #print('\n\ndataset_catalog\n', darray_catalog)

    darray_composite = darray_catalog.mean('datetime', skipna=True)
    #print('\n\ndarray_composite\n', darray_composite)

    nir_path = 'C:/Users/casey/Desktop/nir_composite.png'
    helpers.save_image(darray_composite.sel(band='nir'), nir_path)

    # ds = darray_composite.to_dataset(dim='band')

    return darray_composite


def preprocess_item(item, bands, bbox):
    print(item.metadata['datetime'])

    stack = item.stack_bands(bands)

    darray = stack(chunks=dict(band=1, x=2048, y=2048)).to_dask()
    darray = darray * 0.0001

    darray.coords['scl'] = get_interpolated_scl(item, darray)
    darray = darray.assign_attrs({'crs': item.metadata['proj:epsg']})
    darray['band'] = bands
    #print('\n\ndarray\n', darray)

    darray_clipped = clip(darray, bbox)
    #print('\n\ndarray_clipped\n', darray_clipped)

    darray_masked = cloud_mask_s2(darray_clipped)
    #print('\n\ndarray_masked\n', darray_masked)

    # DEBUG: save plots for image...
    date = str(item.metadata['datetime']).split(' ')[0].replace('-', '_')
    nir_path = 'C:/Users/casey/Desktop/' + date + '.png'
    helpers.save_image(darray_masked.sel(band='nir'), nir_path)

    return darray_masked


