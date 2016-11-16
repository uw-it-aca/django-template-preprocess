from importlib import import_module
from django.template import engines
from django.utils.encoding import smart_text
from fnmatch import fnmatch
import codecs
import re
import os


class Loader(object):
    templates = None

    def get_loaders(self):
        """
        get_loaders from django-compressor
        """
        template_source_loaders = []
        for e in engines.all():
            if hasattr(e, 'engine'):
                template_source_loaders.extend(
                    e.engine.get_template_loaders(e.engine.loaders))
        loaders = []
        # If template loader is CachedTemplateLoader, return the loaders
        # that it wraps around. So if we have
        # TEMPLATE_LOADERS = (
        #    ('django.template.loaders.cached.Loader', (
        #        'django.template.loaders.filesystem.Loader',
        #        'django.template.loaders.app_directories.Loader',
        #    )),
        # )
        # The loaders will return django.template.loaders.filesystem.Loader
        # and django.template.loaders.app_directories.Loader
        # The cached Loader and similar ones include a 'loaders' attribute
        # so we look for that.
        for loader in template_source_loaders:
            if hasattr(loader, 'loaders'):
                loaders.extend(loader.loaders)
            else:
                loaders.append(loader)
        return loaders

    def get_templates(self):
        """ Based on code from django-compressor """
        if Loader.templates:
            return Loader.templates
        extensions = ['html']
        loaders = self.get_loaders()
        templates = {}
        paths = set()
        for loader in loaders:
            try:
                module = import_module(loader.__module__)
                get_template_sources = getattr(module,
                                               'get_template_sources', None)
                if get_template_sources is None:
                    get_template_sources = loader.get_template_sources
                paths.update(smart_text(origin)
                             for origin in get_template_sources(''))
            except (ImportError, AttributeError, TypeError):
                # Yeah, this didn't work out so well, let's move on
                pass

            for path in paths:
                path_templates = set()
                for root, dirs, files in os.walk(path, followlinks=False):
                    path_templates.update(os.path.join(root, name)
                                          for name in files
                                          if not name.startswith('.') and
                                          any(fnmatch(name, "*%s" % glob)
                                          for glob in extensions))

                for full_path in path_templates:
                    partial = full_path.replace(path, "", 1)
                    partial = re.sub('^/+', '', partial)

                    if partial not in templates:
                        templates[partial] = full_path
        Loader.templates = templates
        return templates

    def get_template_path(self, template):
        if not Loader.templates:
            Loader().get_templates()
        return Loader.templates[template]

    def get_template_content(self, template):
        path = self.get_template_path(template)
        with codecs.open(path, encoding="utf-8") as handle:
            content = handle.read()
        return content


def get_templates():
    """
    based on code from django-compressor
    """
    return Loader().get_templates()
