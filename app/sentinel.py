"""app.sentinel: handle requests for Smart Carte"""

from datetime import datetime
import json

from lambda_proxy.proxy import API

from app.sclib import parameters
from app.sclib.utilities import cloud_mask, crop, filter_items_by_bands, get_bands, get_images, limit_items, stack


APP = API(app_name="smart-carte")

@APP.route('/sentinel/search', methods=['GET'], cors=True)
def search():
    query_args = APP.current_request.query_params
    query_args = query_args if isinstance(query_args, dict) else {}

    try:
        valid_args = parameters.validate_parameters(query_args)
    except Exception as e:
        return ('NOK', 'application/json', json.dumps({"message": str(e)}))

    bbox, index = valid_args['bounds'], valid_args['index']
    start, end = valid_args['start'], valid_args['end']

    bands = get_bands(index)
    start_items = limit_items(get_images(bbox, start))
    end_items = limit_items(get_images(bbox, end))
    if len(start_items) == 0 or len(end_items) == 0:
        return ('NOK', 'application/json', json.dumps({'message': 'not enough images'}))

    start_hrefs = filter_items_by_bands(start_items, bands)
    start_cropped = crop(start_hrefs, bbox)
    start_masked = [cloud_mask(item) for item in start_cropped]


    end_hrefs = filter_items_by_bands(end_items, bands)
    end_cropped = crop(end_hrefs, bbox)
    end_masked = [cloud_mask(item) for item in end_cropped]

    return ('OK', 'application/json', json.dumps({
        "start": len(start_items),
        "end": len(end_items)
    }))

