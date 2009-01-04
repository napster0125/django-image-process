import os
from datetime import datetime
from django.conf import settings
from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _

from imagekit.options import Options
from imagekit import specs


class IKModelBase(ModelBase):
    def __init__(cls, name, bases, attrs):
        
        parents = [b for b in bases if isinstance(b, IKModelBase)]
        if not parents:
            return
    
        user_opts = getattr(cls, 'IK', None)
        opts = Options(user_opts)
        
        setattr(cls, '_ik', opts)
        
        try:
            module = __import__(opts.config_module,  {}, {}, [''])
        except ImportError:
            raise ImportError('Unable to load imagekit config module: %s' % opts.config_module)
        
        for spec in [spec for spec in module.__dict__.values() if \
                     issubclass(spec, specs.ImageSpec)]:
            setattr(cls, spec.name, specs.Descriptor(spec))


class IKModel(models.Model):
    """ Abstract base class implementing all core ImageKit functionality
    
    Subclasses of IKModel can override the inner IKConfig class to customize
    storage locations and other options.
    
    """
    __metaclass__ = IKModelBase
    
    CROP_X_NONE   = 0
    CROP_X_LEFT   = 1
    CROP_X_CENTER = 2
    CROP_X_RIGHT  = 3

    CROP_Y_NONE   = 0
    CROP_Y_TOP    = 1
    CROP_Y_CENTER = 2
    CROP_Y_BOTTOM = 3 

    CROP_X_CHOICES = (
        (CROP_X_NONE, 'None'),
        (CROP_X_LEFT, 'Left'),
        (CROP_X_CENTER, 'Center'),
        (CROP_X_RIGHT, 'Right'),
    )

    CROP_Y_CHOICES = (
        (CROP_Y_NONE, 'None'),
        (CROP_Y_TOP, 'Top'),
        (CROP_Y_CENTER,  'Center'),
        (CROP_Y_BOTTOM, 'Bottom'),
    )

    image = models.ImageField(_('image'), upload_to='photos')
    crop_x = models.PositiveSmallIntegerField(choices=CROP_X_CHOICES,
                                              default=CROP_X_CENTER)
    crop_y = models.PositiveSmallIntegerField(choices=CROP_Y_CHOICES,
                                              default=CROP_Y_CENTER)

    class Meta:
        abstract = True
        
    class IK:
        pass
    
    @property        
    def cache_dir(self):
        """ Returns the path to the image cache directory """
        return os.path.join(os.path.dirname(self._obj.image.path),
                            self._ik.cache_dir_name)

    @property
    def cache_url(self):
        """ Returns a url pointing to the image cache directory """
        return '/'.join([os.path.dirname(self._obj.image.url),
                         self._ik.cache_dir_name])
    
    def _cache_spec(self, spec):
        if self._file_exists(spec):
            return
                        
        # create cache directory if it does not exist
        if not os.path.isdir(self._cache_path()):
            os.makedirs(self._cache_path())
            
        img = Image.open(self.image.path)
        
        if img.size != spec.size and spec.size != (0, 0):
            resized = resize_image(img, spec)
            
        output_filename = self._spec_filename(spec)
        
        try:
            if img.format == 'JPEG':
                resized.save(output_filename, img.format, quality=int(spec.quality))
            else:
                try:
                    im.save(im_filename)
                except KeyError:
                    pass
        except IOError, e:
            if os.path.isfile(output_filename):
                os.unlink(output_filename)
            raise e
            
    def _delete_spec(self, spec, remove_dirs=True):
        if not self._file_exists(spec):
            return
        accessor = getattr(self, spec.name)
        if os.path.isfile(accessor.path):
            os.remove(accessor.path)
        if remove_dirs:
            self._cleanupget_cache_dirs
            
    def _cleanup_cache_dirs(self):
        try:
            os.removedirs(self._cache_path())
        except:
            pass

    def _clear_cache(self):
        cache = SpecCache()
        for photosize in cache.sizes.values():
            self._delete_spec(spec, False)
        self._cleanup_cache_dirs()

    def _pre_cache(self):
        cache = SpecCache()
        for spec in cache.specs.values():
            if spec.cache_on_save:
                self._cache_spec(spec)

    def save(self, *args, **kwargs):
        #if self._get_pk_val():
        #    self._clear_cache()
        super(IKModel, self).save(*args, **kwargs)
        #self._pre_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)
        self._clear_cache()
        super(ImageModel, self).delete()
