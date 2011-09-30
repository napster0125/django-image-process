from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string


class AdminThumbnail(object):
    """A convenience utility for adding thumbnails to the Django admin change
    list.

    """
    short_description = _('Thumbnail')
    allow_tags = True

    def __init__(self, image_field, template=None):
        """
        :param image_field: The name of the ImageField or ImageSpec on the model
                to use for the thumbnail.
        :param template: The template with which to render the thumbnail

        """
        self.image_field = image_field
        self.template = template

    def __call__(self, obj):
        thumbnail = getattr(obj, self.image_field, None)
        
        if not thumbnail:
            raise Exception('The property {0} is not defined on {1}.'.format(
                    obj, self.image_field))

        original_image = getattr(thumbnail, 'source_file', None) or thumbnail
        template = self.template or 'imagekit/admin/thumbnail.html'

        return render_to_string(template, {
            'model': obj,
            'thumbnail': thumbnail,
            'original_image': original_image,
        })
