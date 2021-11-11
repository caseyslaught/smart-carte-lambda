
from matplotlib import pyplot
import rasterio


def plot_histogram(array):
    pyplot.hist(array)
    pyplot.show()


def plot_image(image):
    pyplot.imshow(image, cmap='RdYlGn')
    pyplot.show()


def plot_href(href):
    src = rasterio.open(href)
    pyplot.imshow(src.read(1), cmap='pink')
    pyplot.show()


def plot_ndvi(image):
    pyplot.imshow(image, cmap='RdYlGn', vmin=-1, vmax=1)
    pyplot.show()


