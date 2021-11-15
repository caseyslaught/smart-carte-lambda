
from datetime import datetime


from app.sclib import helpers, utilities


virunga = [29.2687, -1.5302, 29.3733, -1.3934] # southern sector
texas = [-100.622848,31.313316,-100.530093,31.398142] # texas
woodstock = [-74.497025, 41.907270, -74.311038, 42.068820]
bbox = virunga

index = 'evi'
bands = utilities.get_bands(index)

start_date = datetime.strptime('2020-10-05T20:06:58.943Z', '%Y-%m-%dT%H:%M:%S.%fZ')
start_catalog = utilities.get_catalog(bbox, start_date)
start_composite = utilities.get_composite_darray(start_catalog, bands, bbox)
start_index = utilities.get_index_darray(start_composite, index)

print(start_index)

start_path = f'C:/Users/casey/Desktop/{index}_start.png'
helpers.save_index(start_index, start_path, index)

end_date = datetime.strptime('2021-10-05T20:06:58.943Z', '%Y-%m-%dT%H:%M:%S.%fZ')
end_catalog = utilities.get_catalog(bbox, end_date)
end_composite = utilities.get_composite_darray(end_catalog, bands, bbox)
end_index = utilities.get_index_darray(end_composite, index)

start_first_y, end_last_y = int(start_index['y'][[0]]), int(end_index['y'][-1])
if start_first_y == end_last_y:
    print('reversing end y coordinate')
    end_index = end_index.reindex({"y": list(reversed(end_index.y))})

print(end_index)

end_path = f'C:/Users/casey/Desktop/{index}_end.png'
helpers.save_index(end_index, end_path, index)

index_diff = end_index - start_index
index_diff_path = f'C:/Users/casey/Desktop/{index}_diff.png'
#helpers.save_image(index_diff, index_diff_path)
helpers.plot_image(index_diff, min=-2, max=2)



