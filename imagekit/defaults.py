""" Default ImageKit configuration """

from imagekit.specs import ImageSpec
from imagekit import processors

class ResizeThumbnail(processors.Crop):
    width = 100
    height = 50

class EnhanceSmall(processors.Adjust):
    contrast = 1.2
    sharpness = 1.1

class SampleReflection(processors.Reflection):
    size = 0.5
    background_color = "#000000"

class PNGFormat(processors.Format):
    format = 'PNG'
    extension = 'png'

class DjangoAdminThumbnail(ImageSpec):
    processors = [ResizeThumbnail(), EnhanceSmall(), SampleReflection(), PNGFormat()]
