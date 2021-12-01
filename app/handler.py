"""app.sentinel: handle requests for Smart Carte"""

import json

import numpy as np

from app.sclib import parameters
from app.sclib.indices import get_bands, get_index_darray
from app.sclib.utilities import get_catalog, get_composite_darray


def handle(event, context):

    bounds = event['bounds']
    start = event['start']
    end = event['end']
    index = event['index']

    try:
        valid_args = parameters.validate_parameters(bounds, start, end, index)
    except Exception as e:
        return {
            'status': 'NOK',
            'message': str(e)
        }

    bbox, index = valid_args['bounds'], valid_args['index']
    start, end = valid_args['start'], valid_args['end']

    bands = get_bands(index)

    start_catalog = get_catalog(bbox, start)
    end_catalog = get_catalog(bbox, end)

    if len(list(start_catalog)) == 0 or len(list(end_catalog)) == 0:
        return {
            'status': 'NOK',
            'message': 'not enough images'
        }

    try:
        start_composite = get_composite_darray(start_catalog, bands, bbox)
    except ValueError:
        return {
            'status': 'NOK',
            'message': 'no start image covers entire bbox'
        }

    start_index = get_index_darray(start_composite, index)

    try:
        end_composite = get_composite_darray(end_catalog, bands, bbox)
    except ValueError:
        return {
            'status': 'NOK',
            'message': 'no end image covers entire bbox'
        }

    end_index = get_index_darray(end_composite, index)

    start_first_y, end_last_y = int(start_index['y'][[0]]), int(end_index['y'][-1])
    if start_first_y == end_last_y:
        print('reversing end y coordinate')
        end_index = end_index.reindex({"y": list(reversed(end_index.y))})

    index_diff = end_index - start_index
    index_diff_mean = np.nanmean(index_diff)

    return {
        'status': 'OK',
        'index': index,
        'mean_change': round(index_diff_mean, 3),
        'image_href': ''
    }


