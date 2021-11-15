
from datetime import datetime, timedelta

import intake_stac
import numpy as np
from pyproj import Proj, transform
from satsearch import Search
from shapely.geometry import Polygon
import xarray as xr

from app.sclib import indices, helpers

IMAGE_LIMIT = 5


def clip(darray, bbox):

    p1 = Proj(init='epsg:4326')
    p2 = Proj(init=f'epsg:{darray.attrs["crs"]}')

    min_lon, max_lat = transform(p1, p2, bbox[0], bbox[3])
    max_lon, min_lat = transform(p1, p2, bbox[2], bbox[1])

    mask_lon = (darray.x >= min_lon) & (darray.x <= max_lon)
    mask_lat = (darray.y >= min_lat) & (darray.y <= max_lat)

    return darray.where(mask_lon & mask_lat, drop=True)


def cloud_mask_s2(darray):
    # 2: dark area; 3: cloud shadows; 7: unclassified; 8: medium cloud; 9: high cloud; 10: cirrus; 11: snow
    mask = np.logical_not(darray.scl.isin([2, 3, 7, 8, 9, 10, 11]))
    return darray.where(mask, drop=True)


def get_bands(index):
    return indices.INDICES[index]


def get_catalog(bbox, target_date):
    
    start = target_date - timedelta(days=30)
    end = target_date + timedelta(days=30)
    date_range = start.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end.strftime('%Y-%m-%dT%H:%M:%SZ')

    search = Search(bbox=bbox, 
                    url='https://earth-search.aws.element84.com/v0',
                    datetime=date_range, 
                    query={'eo:cloud_cover': {'lt': 40}}, 
                    collections=['sentinel-s2-l2a-cogs'],
                    sort=[{"field": "eo:cloudcover", "direction": "asc"}])

    items = search.items() # limit does not work with this provider (pagination issue)
    return intake_stac.catalog.StacItemCollection(items)


def get_interpolated_b05(item, darray):

    da_b05 = item.B05.to_dask()
    da_b05 = da_b05.interp(y=darray['y'], x=darray['x'],
                            kwargs={'fill_value':'extrapolate'},
                            method='nearest').squeeze('band', drop=True)
    da_b05['band'] = 'B05'

    return da_b05


def get_interpolated_scl(item, darray):

    da_scl = item.SCL.to_dask()
    da_scl = da_scl.interp(y=darray['y'], x=darray['x'],
                            kwargs={'fill_value':'extrapolate'},
                            method='nearest').squeeze('band', drop=True)

    return da_scl.compute().astype('uint8')


def get_composite_darray(catalog, bands, bbox):
    
    count, limit = 0, IMAGE_LIMIT
    darray_list = list()
    for id in catalog:
        item = catalog[id]
        processed_item = preprocess_item(item, bands, bbox)
        if processed_item is not None: # None if geometry doesn't contain bbox
            darray_list.append(processed_item)
            count += 1
            if count >= limit:
                break

    darray_catalog = xr.concat(darray_list, 'datetime')
    darray_composite = darray_catalog.mean('datetime', skipna=True)

    return darray_composite


def get_index_darray(darray, index):

    if index == 'ari':
        green = darray.sel(band='B03') + 0.00001
        b05 = darray.sel(band='B05') + 0.00001
        return 1.0 / green - 1.0 / b05

    elif index == 'evi':
        blue = darray.sel(band='B02')
        nir = darray.sel(band='B08')
        red = darray.sel(band='B04')
        return 2.5 * (nir - red) / ((nir + 6.0 * red - 7.5 * blue) + 1.0)

    elif index == 'ndvi':
        nir = darray.sel(band='B08')
        red = darray.sel(band='B04')
        return (nir - red) / (nir + red)

    elif index == 'ndwi':
        nir = darray.sel(band='B08')
        green = darray.sel(band='B03')
        return (green - nir) / (green + nir)

    else:
        raise ValueError('index not found')


def is_bbox_contained(bbox, geometry):
    """
    bbox = [29.2687, -1.5302, 29.3733, -1.3934]
    geometry = [
        [
            [29.783617891437096, -1.53565136283662], 
            [29.782378516359515, -1.5354718843255077], 
            [28.798530645813006, -1.3303892797450998], 
            [28.797823053383, -0.903929667152524], 
            [29.782967842321614, -0.9033041474033248], 
            [29.783617891437096, -1.53565136283662]
        ]
    ]
    """

    bbox_tl = (bbox[0], bbox[3])
    bbox_tr = (bbox[2], bbox[3])
    bbox_br = (bbox[2], bbox[1])
    bbox_bl = (bbox[0], bbox[1])

    outer_points = [(p[0], p[1]) for p in geometry[0]]

    poly_inner = Polygon([bbox_tl, bbox_tr, bbox_br, bbox_bl]) 
    poly_outer = Polygon(outer_points) 

    return poly_outer.contains(poly_inner)

    
def preprocess_item(item, bands, bbox):
    print(item.metadata['datetime'])

    geometry = item.metadata['geometry']['coordinates']
    if not is_bbox_contained(bbox, geometry):
        return None

    stack_bands = [b for b in bands if b not in ['B05']]
    is_b05 = len(stack_bands) != len(bands)

    stack = item.stack_bands(stack_bands)
    darray = stack(chunks=dict(band=1, x=2048, y=2048)).to_dask()

    if is_b05:
        darray_b05 = get_interpolated_b05(item, darray)
        darray = xr.concat([darray, darray_b05], dim='band')

    darray = darray * 0.0001

    darray.coords['scl'] = get_interpolated_scl(item, darray)
    darray = darray.assign_attrs({'crs': item.metadata['proj:epsg']})

    darray_clipped = clip(darray, bbox)
    darray_masked = cloud_mask_s2(darray_clipped)

    return darray_masked


