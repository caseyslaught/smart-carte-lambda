
from datetime import datetime, timedelta

import numpy as np
import numpy.ma as ma
from pyproj import Proj, transform
import rasterio
from satsearch import Search

from app.sclib import indices


def clip(darray, bbox):
    p1 = Proj(init='epsg:4326')
    p2 = Proj(init=f'epsg:{darray.attrs["crs"]}')

    min_lon, max_lat = transform(p1, p2, bbox[0], bbox[3])
    max_lon, min_lat = transform(p1, p2, bbox[2], bbox[1])

    print(min_lon, max_lat)
    print(max_lon, min_lat)

    mask_lon = (darray.x >= min_lon) & (darray.x <= max_lon)
    mask_lat = (darray.y >= min_lat) & (darray.y <= max_lat)

    return darray.where(mask_lon & mask_lat, drop=True)


def cloud_mask_s2(darray):
    # 3: cloud shadows; 8: medium cloud; 9: high cloud
    mask = np.logical_not(darray.scl.isin([3, 8, 9]))
    return darray.where(mask, drop=True)



def cloud_mask(item_dict):
    # 3	CLOUD_SHADOWS
    # 8	CLOUD_MEDIUM_PROBABILITY
    # 9 CLOUD_HIGH_PROBABILITY

    scl = item_dict.pop('SCL')
    mask = np.isin(scl, [3, 8, 9]) # masked expect True for masked things

    masked_dict = dict()
    for band, subset in item_dict.items():
        subset, mask = fit_array(subset, mask)
        masked_dict[band] = ma.masked_array(subset, mask)

    return masked_dict


def crop(href_list, bbox):

    cropped_list = list()
    for href_dict in href_list:
        cropped_dict = dict()
        for band, href in href_dict.items():
            with rasterio.open(href) as dataset:

                p1 = Proj(init='epsg:4326')
                p2 = Proj(init=dataset.crs)
                top_left = transform(p1, p2, bbox[0], bbox[3])
                bottom_right = transform(p1, p2, bbox[2], bbox[1])

                pixel_top_left = dataset.index(top_left[0], top_left[1])
                pixel_bottom_right = dataset.index(bottom_right[0], bottom_right[1])

                # if it fails for one band, it should fail for all others, right?
                # making sure the bbox (frontend validation) ensures this rarely happens
                outside = [True for pixel in pixel_top_left + pixel_bottom_right if pixel < 0]
                if len(outside) > 0:
                    print('Bbox extends image extents. Skipping band.')
                    continue

                window = rasterio.windows.Window.from_slices(
                    (pixel_top_left[0], pixel_bottom_right[0]), 
                    (pixel_top_left[1], pixel_bottom_right[1]))

                subset = dataset.read(1, window=window)

                if band == 'SCL':
                    subset = np.repeat(np.repeat(subset, 2, axis=0), 2, axis=1)

                cropped_dict[band] = subset

        cropped_list.append(cropped_dict)

    return cropped_list


def filter_items_by_bands(items_list, bands):
    items = list()
    for item in items_list:
        items.append({
            band: item.asset(band)['href']
            for band in bands
        })

    return items


def fit_array(a, b):
    a_rows, a_cols = a.shape
    b_rows, b_cols = b.shape

    min_rows = min(a_rows, b_rows)
    min_cols = min(a_cols, b_cols)

    return a[:min_rows, :min_cols], b[:min_rows, :min_cols]


def get_bands(index):
    return indices.INDICES.get(index, indices.INDICES['ndvi'])


def get_images(bbox, target_date):
    
    start = target_date - timedelta(days=21)
    end = target_date + timedelta(days=21)
    date_range = start.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end.strftime('%Y-%m-%dT%H:%M:%SZ')

    search = Search(bbox=bbox, 
                    url='https://earth-search.aws.element84.com/v0',
                    datetime=date_range, 
                    query={'eo:cloud_cover': {'lt': 30}}, 
                    collections=['sentinel-s2-l2a-cogs'],
                    sort=[{"field": "eo:cloud_cover", "direction": "asc"}])

    items = search.items() # limit does not work
    return items 


def get_interpolated_scl(item, darray):
    da_scl = item.SCL.to_dask()
    da_scl = da_scl.interp(y=darray['y'], x=darray['x'],
                            kwargs={'fill_value':'extrapolate'},
                            method='nearest').squeeze('band', drop=True)

    return da_scl.compute().astype('uint8')


def limit_items(item_collection):
    return item_collection[:5] # limit doesn't work so enforcing limit here (converts to list)


def stack(item):

    idx = 0
    images = list()
    layers = dict()
    for band, image in item.items():
        images.append(image)
        layers[band] = idx
        idx += 1

    return {
        'stack': np.dstack(images),
        'layers': layers
    }


def test_crop(href, bbox):

    with rasterio.open(href) as dataset:
        p1 = Proj(init='epsg:4326')
        p2 = Proj(init=dataset.crs)

        top_left = transform(p1, p2, bbox[0], bbox[3])
        bottom_right = transform(p1, p2, bbox[2], bbox[1])

        pixel_top_left = dataset.index(top_left[0], top_left[1])
        pixel_bottom_right = dataset.index(bottom_right[0], bottom_right[1])

        print(top_left, bottom_right)
        print(pixel_top_left, pixel_bottom_right)
        
        window = rasterio.windows.Window.from_slices(
            (pixel_top_left[0], pixel_bottom_right[0]), 
            (pixel_top_left[1], pixel_bottom_right[1]))

        return dataset.read(1, window=window)

