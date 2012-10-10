import os

from django.db import models
from ..files import ProcessedImageFieldFile
from .utils import ImageSpecFileDescriptor
from ..receivers import configure_receivers
from ...utils import suggest_extension
from ...specs import SpecHost, spec_registry
from ...specs.sources import ImageFieldSpecSource


class ImageSpecField(SpecHost):
    """
    The heart and soul of the ImageKit library, ImageSpecField allows you to add
    variants of uploaded images to your models.

    """
    def __init__(self, processors=None, format=None, options=None,
        image_field=None, storage=None, autoconvert=None,
        image_cache_backend=None, image_cache_strategy=None, spec=None,
        id=None):

        # The spec accepts a callable value for processors, but it
        # takes different arguments than the callable that ImageSpecField
        # expects, so we create a partial application and pass that instead.
        # TODO: Should we change the signatures to match? Even if `instance` is not part of the signature, it's accessible through the source file object's instance property.
        p = lambda file: processors(instance=file.instance,
                file=file) if callable(processors) else processors

        SpecHost.__init__(self, processors=p, format=format,
                options=options, storage=storage, autoconvert=autoconvert,
                image_cache_backend=image_cache_backend,
                image_cache_strategy=image_cache_strategy, spec=spec,
                spec_id=id)

        self.image_field = image_field

    @property
    def storage(self):
        return self.spec.storage

    def contribute_to_class(self, cls, name):
        setattr(cls, name, ImageSpecFileDescriptor(self, name))

        # Generate a spec_id to register the spec with. The default spec id is
        # "<app>:<model>_<field>"
        if not getattr(self, 'spec_id', None):
            self.spec_id = (u'%s:%s_%s' % (cls._meta.app_label,
                    cls._meta.object_name, name)).lower()

            # Register the spec with the id. This allows specs to be overridden
            # later, from outside of the model definition.
            self.set_spec_id(self.spec_id)

        # Register the model and field as a source for this spec id
        spec_registry.add_source(self.spec_id,
                                 ImageFieldSpecSource(cls, self.image_field))


class ProcessedImageField(models.ImageField, SpecHost):
    """
    ProcessedImageField is an ImageField that runs processors on the uploaded
    image *before* saving it to storage. This is in contrast to specs, which
    maintain the original. Useful for coercing fileformats or keeping images
    within a reasonable size.

    """
    attr_class = ProcessedImageFieldFile

    def __init__(self, processors=None, format=None, options=None,
        verbose_name=None, name=None, width_field=None, height_field=None,
        autoconvert=True, spec=None, spec_id=None, **kwargs):
        """
        The ProcessedImageField constructor accepts all of the arguments that
        the :class:`django.db.models.ImageField` constructor accepts, as well
        as the ``processors``, ``format``, and ``options`` arguments of
        :class:`imagekit.models.ImageSpecField`.

        """
        SpecHost.__init__(self, processors=processors, format=format,
                options=options, autoconvert=autoconvert, spec=spec,
                spec_id=spec_id)
        models.ImageField.__init__(self, verbose_name, name, width_field,
                height_field, **kwargs)

    def get_filename(self, filename):
        filename = os.path.normpath(self.storage.get_valid_name(
                os.path.basename(filename)))
        name, ext = os.path.splitext(filename)
        ext = suggest_extension(filename, self.spec.format)
        return u'%s%s' % (name, ext)


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], [r'^imagekit\.models\.fields\.ProcessedImageField$'])


configure_receivers()
