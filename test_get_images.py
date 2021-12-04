
from datetime import datetime

import numpy as np

from app.sclib import indices, utilities


fence = [29.526019, -0.860236, 29.600013, -0.760466]
southern = [29.2687, -1.5302, 29.3733, -1.3934]
nyiragongo = [29.186988, -1.610626, 29.406452, -1.462159] 
texas = [-100.622848,31.313316,-100.530093,31.398142]
woodstock = [-74.4349121, 41.9010394, -74.3296504, 41.9973306]

start_string = '2017-10-10T20:06:58.943Z'
end_string = '2021-10-10T20:06:58.943Z'

bbox = fence

index = 'arvi'
bands = indices.get_bands(index)

start_date = datetime.strptime(start_string, '%Y-%m-%dT%H:%M:%S.%fZ')
start_catalog = utilities.get_catalog(bbox, start_date)
print(list(start_catalog))
start_composite = utilities.get_composite_darray(start_catalog, bands, bbox)
start_index = indices.get_index_darray(start_composite, index)

#start_path = f'C:/Users/casey/Desktop/{index}_start.png'
#helpers.save_index(start_index, start_path, index)

end_date = datetime.strptime(end_string, '%Y-%m-%dT%H:%M:%S.%fZ')
end_catalog = utilities.get_catalog(bbox, end_date)
print(list(end_catalog))
end_composite = utilities.get_composite_darray(end_catalog, bands, bbox)
end_index = indices.get_index_darray(end_composite, index)

start_first_y, end_last_y = int(start_index['y'][[0]]), int(end_index['y'][-1])
if start_first_y == end_last_y:
    print('reversing end y coordinate')
    end_index = end_index.reindex({"y": list(reversed(end_index.y))})

#end_path = f'C:/Users/casey/Desktop/{index}_end.png'
#helpers.save_index(end_index, end_path, index)

index_diff = end_index - start_index

print(index_diff)

cloud_count = np.count_nonzero(np.isnan(index_diff))
shape = index_diff.shape

cloud_area_ha = cloud_count / 100
total_area_ha = shape[0] * shape[1] / 100

print(cloud_area_ha, total_area_ha)
print(cloud_area_ha / total_area_ha)


# TODO: how to interpret index mean as percentage increase?
#print(index_diff)
#print('difference mean:', np.nanmean(index_diff))

# index_diff_path = f'C:/Users/casey/Desktop/{index}_diff.png'
# helpers.save_image(index_diff, index_diff_path)
# helpers.plot_image(index_diff, min=-2, max=2)

