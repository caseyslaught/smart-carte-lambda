"""app.sentinel: handle requests for Smart Carte"""

from datetime import datetime
import json

from lambda_proxy.proxy import API

import indices


APP = API(app_name="smart-carte")

@APP.route('/sentinel/search', methods=['GET'], cors=True)
def search():
    query_args = APP.current_request.query_params
    query_args = query_args if isinstance(query_args, dict) else {}

    required_args = ['bounds', 'start', 'end', 'index']
    if not all(arg in query_args.keys() for arg in required_args):
        return ('Bad Request', 'application/json', 
                json.dumps({"message": "query argument(s) missing: bounds, start, end, index"}))

    try:
        bounds = query_args['bounds'].split(',')
        bounds = [float(b) for b in bounds]
    except:
        return ('Bad Request', 'application/json', json.dumps({"message": "invalid bounds parameter"}))

    try:
        start = query_args['start']
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        return ('Bad Request', 'application/json', json.dumps({"message": "invalid start parameter"}))

    try:
        end = query_args['end']
        end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        return ('Bad Request', 'application/json', json.dumps({"message": "invalid start parameter"}))

    index = query_args['index']
    if index not in indices.INDICES.keys():
        return ('Bad Request', 'application/json', json.dumps({"message": "invalid index parameter"}))

    return ('OK', 'application/json', json.dumps({"hello": "world!"}))

