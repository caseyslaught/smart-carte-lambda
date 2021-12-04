"""app.sentinel: handle requests for Smart Carte"""

from datetime import datetime
import json

from lambda_proxy.proxy import API
import numpy as np

from app.sclib import parameters
from app.sclib.indices import get_bands, get_index_darray
from app.sclib.utilities import get_catalog, get_composite_darray


APP = API(name="smart-carte")

@APP.route('/search', methods=['GET'], cors=True)
def search(bounds=None, start=None, end=None, index=None):

    try:
        valid_args = parameters.validate_parameters(bounds, start, end, index)
    except Exception as e:
        return ('NOK', 'application/json', json.dumps({"message": str(e)}))

    bbox, index = valid_args['bounds'], valid_args['index']
    start, end = valid_args['start'], valid_args['end']

    bands = get_bands(index)

    start_catalog = get_catalog(bbox, start)
    end_catalog = get_catalog(bbox, end)

    if len(list(start_catalog)) == 0 or len(list(end_catalog)) == 0:
        return ('NOK', 'application/json', json.dumps({'message': 'not enough images'}))

    try:
        start_composite = get_composite_darray(start_catalog, bands, bbox)
    except ValueError:
        return ('NOK', 'application/json', json.dumps({'message': 'no start image covers entire bbox'}))

    start_index = get_index_darray(start_composite, index)

    try:
        end_composite = get_composite_darray(end_catalog, bands, bbox)
    except ValueError:
        return ('NOK', 'application/json', json.dumps({'message': 'no end image covers entire bbox'}))

    end_index = get_index_darray(end_composite, index)

    start_first_y, end_last_y = int(start_index['y'][[0]]), int(end_index['y'][-1])
    if start_first_y == end_last_y:
        print('reversing end y coordinate')
        end_index = end_index.reindex({"y": list(reversed(end_index.y))})

    index_diff = end_index - start_index
    index_change = np.nanmean(index_diff)

    cloud_count = np.count_nonzero(np.isnan(index_diff))
    shape = index_diff.shape

    cloud_area_ha = cloud_count / 100
    total_area_ha = shape[0] * shape[1] / 100

    return ('OK', 'application/json', json.dumps({
        'index': index,
        'total_area_ha': total_area_ha,
        'cloud_area_ha': cloud_area_ha,
        'index_change': round(index_change, 4),
        'image_href': ''
    }))
