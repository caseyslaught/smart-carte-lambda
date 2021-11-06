
from datetime import datetime, timedelta

from pyproj import Transformer
import rasterio
from satsearch import Search

import indices


def crop(href_list, bbox):

    cropped_list = list()
    for href_dict in href_list:
        cropped_dict = dict()
        for band, href in href_dict.items():
            print(band)
            with rasterio.open(href) as dataset:

                transformer = Transformer.from_crs("epsg:4326", dataset.crs, always_xy=True)
                top_left = transformer.transform(bbox[0], bbox[3])
                bottom_right = transformer.transform(bbox[2], bbox[1])

                pixel_top_left = dataset.index(top_left[0], top_left[1])
                pixel_bottom_right = dataset.index(bottom_right[0], bottom_right[1])

                print(top_left, bottom_right)
                print(pixel_top_left, pixel_bottom_right)

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
                cropped_dict[band] = subset

        cropped_list.append(cropped_dict)

    return cropped_list


def filter_items_by_bands(item_collection, bands):
    items = list()
    for item in item_collection:
        items.append({
            band: item.asset(band)['href']
            for band in bands
        })

    return items


def get_bands(index):
    return indices.INDICES.get(index, indices.INDICES['ndvi'])


def get_images(bbox, date):
    target = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') # 2021-11-05T20:06:58.943Z

    start = target - timedelta(days=21)
    end = target + timedelta(days=21)
    date_range = start.strftime('%Y-%m-%dT%H:%M:%SZ') + '/' + end.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(bbox, date_range)

    search = Search(bbox=bbox, 
                    url='https://earth-search.aws.element84.com/v0',
                    datetime=date_range, 
                    query={'eo:cloud_cover': {'lt': 30}}, 
                    collections=['sentinel-s2-l2a-cogs'])

    items = search.items() # [satstac.item.Item]
    print(type(items))
    print(items.summary())
    return items


def test_crop(href, bbox):


    with rasterio.open(href) as dataset:
        print(dataset.crs)
        transformer = Transformer.from_crs("epsg:4326", dataset.crs, always_xy=True)
        top_left = transformer.transform(bbox[0], bbox[3])
        bottom_right = transformer.transform(bbox[2], bbox[1])

        pixel_top_left = dataset.index(top_left[0], top_left[1])
        pixel_bottom_right = dataset.index(bottom_right[0], bottom_right[1])

        print(top_left, bottom_right)
        print(pixel_top_left, pixel_bottom_right)
        
        window = rasterio.windows.Window.from_slices(
            (pixel_top_left[0], pixel_bottom_right[0]), 
            (pixel_top_left[1], pixel_bottom_right[1]))

        return dataset.read(1, window=window)
