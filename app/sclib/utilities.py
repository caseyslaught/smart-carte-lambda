
from datetime import timedelta

import intake_stac
import numpy as np
from pyproj import Proj, transform
from satsearch import Search
from shapely.geometry import Polygon
import xarray as xr


CLOUD_COVER_MAX = 40
IMAGE_LIMIT = 4
PADDING_DAYS = 30


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


def get_catalog(bbox, target_date):
    
    start = target_date - timedelta(days=PADDING_DAYS)
    end = target_date + timedelta(days=PADDING_DAYS)
    date_range = start.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end.strftime('%Y-%m-%dT%H:%M:%SZ')

    search = Search(bbox=bbox, 
                    url='https://earth-search.aws.element84.com/v0',
                    datetime=date_range, 
                    query={'eo:cloud_cover': {'lt': CLOUD_COVER_MAX}}, 
                    collections=['sentinel-s2-l2a-cogs'],
                    sort=[{"field": "eo:cloudcover", "direction": "asc"}])

    items = search.items() # limit does not work with this provider (pagination issue)
    return intake_stac.catalog.StacItemCollection(items)


def get_interpolated_band(item, darray, band):

    if band == 'B05':
        da = item.B05.to_dask()
    elif band == 'B06':
        da = item.B06.to_dask()
    elif band == 'B07':
        da = item.B07.to_dask()
    elif band == 'B8A':
        da = item.B8A.to_dask()
    elif band == 'B09':
        da = item.B09.to_dask()
    elif band == 'B11':
        da = item.B11.to_dask()
    elif band == 'B12':
        da = item.B12.to_dask()
    else:
        raise ValueError('band not supported')

    da = da.interp(y=darray['y'], x=darray['x'],
                            kwargs={'fill_value':'extrapolate'},
                            method='nearest').squeeze('band', drop=True)
    da['band'] = band

    return da


def get_interpolated_scl(item, darray):

    da_scl = item.SCL.to_dask()
    da_scl = da_scl.interp(y=darray['y'], x=darray['x'],
                            kwargs={'fill_value':'extrapolate'},
                            method='nearest').squeeze('band', drop=True)

    return da_scl.compute().astype('uint8')


def get_composite_darray(catalog, bands, bbox):
    
    # TODO: sometimes there are two images for the same time, maybe skip if already added to darray_list

    count, limit = 0, IMAGE_LIMIT
    darray_list = list()
    previous_datetimes = list()
    for id in catalog:
        item = catalog[id]
        item_datetime = item.metadata['datetime']
        if item_datetime not in previous_datetimes:
            processed_item = preprocess_item(item, bands, bbox)
            if processed_item is not None: # None if geometry doesn't contain bbox
                previous_datetimes.append(item_datetime)
                darray_list.append(processed_item)
                count += 1
                if count >= limit:
                    break
    
    if len(darray_list) == 0:
        raise ValueError('darray_list is empty, probably due to geometry')

    darray_catalog = xr.concat(darray_list, 'datetime')
    darray_composite = darray_catalog.mean('datetime', skipna=True)

    return darray_composite


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
        print('bbox not contained by image geometry')
        return None

    different_gsd_bands = ['B05', 'B06', 'B07', 'B8A', 'B09', 'B11', 'B12']
    stack_bands = [b for b in bands if b not in different_gsd_bands]
    excluded_bands = [b for b in bands if b in different_gsd_bands]

    stack = item.stack_bands(stack_bands)
    darray = stack(chunks=dict(band=1, x=2048, y=2048)).to_dask()

    for ex_band in excluded_bands:
        darray_ex = get_interpolated_band(item, darray, ex_band)
        darray = xr.concat([darray, darray_ex], dim='band')

    darray = darray * 0.0001

    darray.coords['scl'] = get_interpolated_scl(item, darray)
    darray = darray.assign_attrs({'crs': item.metadata['proj:epsg']})

    darray_clipped = clip(darray, bbox)
    darray_masked = cloud_mask_s2(darray_clipped)

    return darray_masked


