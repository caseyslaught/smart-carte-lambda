
from matplotlib import pyplot
import numpy as np
import rasterio


def plot_histogram(array):
    pyplot.hist(array)
    pyplot.show()
    pyplot.cla()
    pyplot.clf()


def plot_image(image):
    pyplot.imshow(image, cmap='RdYlGn')
    pyplot.show()
    pyplot.cla()
    pyplot.clf()


def plot_href(href):
    src = rasterio.open(href)
    pyplot.imshow(src.read(1), cmap='pink')
    pyplot.show()
    pyplot.cla()
    pyplot.clf()


def plot_index(image, index):

    min, max = -1, 1
    if index == 'ari':
        min, max = -10, 10

    pyplot.imshow(image, cmap='RdYlGn', vmin=min, vmax=max)
    pyplot.show()
    pyplot.cla()
    pyplot.clf()


def save_image(image, path):
    pyplot.imshow(image, cmap='RdYlGn')
    pyplot.savefig(path)
    pyplot.cla()
    pyplot.clf()


def save_index(image, path, index):

    min, max = -1, 1
    if index == 'ari':
        min, max = -10, 10

    pyplot.imshow(image, cmap='RdYlGn', vmin=min, vmax=max)
    pyplot.savefig(path)
    pyplot.cla()
    pyplot.clf()


def save_rgb(image, path):

    # TODO: add scaling 
    R = image.sel(band='B04')
    G = image.sel(band='B03')
    B = image.sel(band='B02')
    RGB = np.dstack([R, G, B])

    pyplot.imshow(RGB)
    pyplot.savefig(path)
    pyplot.cla()
    pyplot.clf()



    