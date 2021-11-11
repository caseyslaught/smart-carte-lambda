
from app.sclib import parameters


args = {
    'bounds': '29.2687,-1.5302,29.3733,-1.3934',
    'start': '2021-02-10T10:23:10.123Z',
    'end': '2021-06-10T10:23:10.123Z',
    'index': 'ndvi'
}

try:
    args = parameters.validate_parameters(args)
    print(args)
except Exception as e:
    print(str(e))

