
from datetime import datetime

from app.sclib import indices


REQUIRED = ['bounds', 'start', 'end', 'index']


def validate_parameters(bounds, start, end, index):

    if None in [bounds, start, end, index]:
        raise Exception('query argument(s) missing: bounds, start, end, index')

    parameters = dict()

    try:
        bounds = bounds.split(',') # TODO: more validation...
        parameters['bounds'] = [float(b) for b in bounds]
    except:
        raise Exception('invalid bounds parameter')

    try:
        parameters['start'] = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        raise Exception('invalid start parameter')

    try:
        parameters['end'] = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        raise Exception('invalid end parameter')

    try:
        assert index in indices.INDICES.keys()
        parameters['index'] = index
    except:
        raise Exception('invalid index parameter')

    return parameters
    
