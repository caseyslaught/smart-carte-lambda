

INDICES = {
    'ari': ['green', 'B05'],
    'arvi': ['blue', 'red', 'B8A'],
    'evi': ["blue", "red", "nir"],
    'exgi': ['blue', 'green', 'red'],
    'gndvi': ['green', 'nir'],
    'ndvi': ["red", "nir"],
    'ndwi': ['green', 'nir'],
    'psri': ['blue', 'red', 'B06'],
    'true': ["blue", "green", "red"],
}


def get_bands(index):
    return INDICES[index]


def get_index_darray(darray, index):

    if index == 'ari':
        green = darray.sel(band='B03') + 0.00001
        b05 = darray.sel(band='B05') + 0.00001
        return 1.0 / green - 1.0 / b05

    elif index == 'arvi':
        y = 0.106
        blue = darray.sel(band='B02')
        red = darray.sel(band='B04')
        b8A = darray.sel(band='B8A')
        return (b8A - red - y * (red - blue)) / (b8A + red - y * (red - blue))

    elif index == 'evi':
        blue = darray.sel(band='B02')
        red = darray.sel(band='B04')
        nir = darray.sel(band='B08')
        return 2.5 * (nir - red) / ((nir + 6.0 * red - 7.5 * blue) + 1.0)

    elif index == 'exgi':
        blue = darray.sel(band='B02')
        green = darray.sel(band='B03')
        red = darray.sel(band='B04')
        return (2 * green) - (red + blue)

    elif index == 'gndvi':
        green = darray.sel(band='B03')
        nir = darray.sel(band='B08')
        return (nir - green) / (nir + green)

    elif index == 'ndvi':
        nir = darray.sel(band='B08')
        red = darray.sel(band='B04')
        return (nir - red) / (nir + red)

    elif index == 'ndwi':
        nir = darray.sel(band='B08')
        green = darray.sel(band='B03')
        return (green - nir) / (green + nir)

    elif index == 'psri':
        blue = darray.sel(band='B02')
        red = darray.sel(band='B04')
        b06 = darray.sel(band='B06')
        return (red - blue) / b06

    else:
        raise ValueError('index not found')



