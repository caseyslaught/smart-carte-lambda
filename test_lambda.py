import json
import os
import time


from app.handler import handle


event = {
    'bounds': '29.2687,-1.5302,29.3733,-1.3934',
    'start': '2020-10-10T20:06:58.943Z',
    'end': '2021-10-10T20:06:58.943Z',
    'index': 'ndvi'
}

start_time = time.time()
res = handle(event, None)
print('res', json.dumps(res))
print("--- %0.2f seconds ---" % (time.time() - start_time))

