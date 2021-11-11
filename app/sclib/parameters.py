
from datetime import datetime

from app.sclib import indices


REQUIRED = ['bounds', 'start', 'end', 'index']


def validate_parameters(parameters):

    if not all(arg in parameters.keys() for arg in REQUIRED):
        raise Exception('query argument(s) missing: bounds, start, end, index')

    try:
        bounds = parameters['bounds'].split(',')
        parameters['bounds'] = [float(b) for b in bounds]
    except:
        raise Exception('invalid bounds parameter')

    try:
        start = parameters['start']
        parameters['start'] = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        raise Exception('invalid start parameter')

    try:
        end = parameters['end']
        parameters['end'] = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        raise Exception('invalid end parameter')

    try:
        index = parameters['index']
        assert index in indices.INDICES.keys()
    except:
        raise Exception('invalid index parameter')

    return parameters
    
