
from datetime import datetime

import helpers
import utilities


bbox = [29.2687, -1.5302, 29.3733, -1.3934]

items = utilities.get_images(bbox, '2021-10-05T20:06:58.943Z')

items.save('test.json')



bands = utilities.get_bands("ndvi")

filtered_items = utilities.filter_items_by_bands(items, bands)
print(filtered_items)

cropped_items = utilities.crop(filtered_items, bbox)
print(cropped_items)


#href = filtered_items[0]['red']
#subset = utilities.test_crop(href, bbox)
#helpers.plot_href(href)
#helpers.plot_image(subset)



