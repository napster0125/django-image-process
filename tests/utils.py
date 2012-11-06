import os

from django.core.files.base import ContentFile

from imagekit.lib import Image, StringIO
from .models import Photo
import pickle


def get_image_file():
    """
    See also:

    http://en.wikipedia.org/wiki/Lenna
    http://sipi.usc.edu/database/database.php?volume=misc&image=12

    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'lenna-800x600-white-border.jpg')
    tmp = StringIO()
    tmp.write(open(path, 'r+b').read())
    tmp.seek(0)
    return tmp


def create_image():
    return Image.open(get_image_file())


def create_instance(model_class, image_name):
    instance = model_class()
    img = get_image_file()
    file = ContentFile(img.read())
    instance.original_image = file
    instance.original_image.save(image_name, file)
    instance.save()
    img.close()
    return instance


def create_photo(name):
    return create_instance(Photo, name)


def pickleback(obj):
    pickled = StringIO()
    pickle.dump(obj, pickled)
    pickled.seek(0)
    return pickle.load(pickled)
