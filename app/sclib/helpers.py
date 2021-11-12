
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

def plot_ndvi(image):
    pyplot.imshow(image, cmap='RdYlGn', vmin=-1, vmax=1)
    pyplot.show()
    pyplot.cla()
    pyplot.clf()

def save_image(image, path):
    pyplot.imshow(image, cmap='RdYlGn')
    pyplot.savefig(path)
    pyplot.cla()
    pyplot.clf()


def save_ndvi(image, path):
    pyplot.imshow(image, cmap='RdYlGn', vmin=-1, vmax=1)
    pyplot.savefig(path)
    pyplot.cla()
    pyplot.clf()


def save_rgb(image, path):

    # TODO: add scaling 
    R = image.sel(band='red')
    G = image.sel(band='green')
    B = image.sel(band='blue')
    RGB = np.dstack([R, G, B])

    pyplot.imshow(RGB)
    pyplot.savefig(path)
    pyplot.cla()
    pyplot.clf()



    