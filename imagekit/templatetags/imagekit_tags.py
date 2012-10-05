import os
from django import template
from django.utils.safestring import mark_safe

from ..exceptions import AlreadyRegistered, NotRegistered
from ..files import ImageSpecFile


register = template.Library()


class SpecRegistry(object):
    def __init__(self):
        self._specs = {}

    def register(self, id, spec):
        if id in self._specs:
            raise AlreadyRegistered('The spec with id %s is already registered' % id)
        self._specs[id] = spec

    def unregister(self, id, spec):
        try:
            del self._specs[id]
        except KeyError:
            raise NotRegistered('The spec with id %s is not registered' % id)

    def get_spec(self, id):
        try:
            return self._specs[id]
        except KeyError:
            raise NotRegistered('The spec with id %s is not registered' % id)


spec_registry = SpecRegistry()


class ImageSpecFileHtmlWrapper(object):
    def __init__(self, image_spec_file):
        self._image_spec_file = image_spec_file

    def __getattr__(self, name):
        return getattr(self._image_spec_file, name)

    def __unicode__(self):
        return mark_safe(u'<img src="%s" />' % self.url)


class SpecNode(template.Node):
    def __init__(self, spec_id, source_image, variable_name=None):
        self.spec_id = spec_id
        self.source_image = source_image
        self.variable_name = variable_name

    def render(self, context):
        from ..utils import autodiscover
        autodiscover()
        source_image = self.source_image.resolve(context)
        spec_id = self.spec_id.resolve(context)
        spec = spec_registry.get_spec(spec_id)
        if callable(spec):
            spec = spec()
        spec_file = ImageSpecFileHtmlWrapper(ImageSpecFile(spec, source_image, spec_id))
        if self.variable_name is not None:
            variable_name = str(self.variable_name)
            context[variable_name] = spec_file
            return ''

        return spec_file


#@register.tag
# TODO: Should this be renamed to something like 'process'?
def spec(parser, token):
    """
    Creates an image based on the provided spec and source image.

    By default::

        {% spec 'myapp:thumbnail', mymodel.profile_image %}

    Generates an ``<img>``::

        <img src="/cache/34d944f200dd794bf1e6a7f37849f72b.jpg" />

    Storing it as a context variable allows more flexibility::

        {% spec 'myapp:thumbnail' mymodel.profile_image as th %}
        <img src="{{ th.url }}" width="{{ th.width }}" height="{{ th.height }}" />

    """

    args = token.split_contents()
    arg_count = len(args)

    if (arg_count < 3 or arg_count > 5
        or (arg_count > 3 and arg_count < 5)
        or (args == 5 and args[3] != 'as')):
        raise template.TemplateSyntaxError('\'spec\' tags must be in the form'
                                           ' "{% spec spec_id image %}" or'
                                           ' "{% spec spec_id image'
                                           ' as varname %}"')

    spec_id = parser.compile_filter(args[1])
    source_image = parser.compile_filter(args[2])
    variable_name = arg_count > 3 and args[4] or None
    return SpecNode(spec_id, source_image, variable_name)


spec = spec_tag = register.tag(spec)


def _register_spec(id, spec=None):
    if not spec:
        def decorator(cls):
            spec_registry.register(id, cls)
            return cls
        return decorator
    spec_registry.register(id, spec)


def _unregister_spec(id, spec):
    spec_registry.unregister(id, spec)


spec_tag.register = _register_spec
spec_tag.unregister = _unregister_spec
