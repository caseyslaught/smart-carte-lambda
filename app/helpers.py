
from matplotlib import pyplot
import rasterio


def plot_image(image):
    pyplot.imshow(image, cmap='pink')
    pyplot.show()


def plot_href(href):
    src = rasterio.open(href)
    pyplot.imshow(src.read(1), cmap='pink')
    pyplot.show()




