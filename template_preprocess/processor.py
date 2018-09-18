from django.conf import settings
from importlib import import_module

from template_preprocess.util.loader import Loader
from template_preprocess.util.content_type import filename_is_html


def process_sub_template(name, seen_templates):
    content = Loader().get_template_content(name)
    is_html = filename_is_html(name)
    return process_template_content(content,
                                    seen_templates,
                                    subcall=True,
                                    is_html=is_html)


def process_template_content(content,
                             seen_templates=None,
                             subcall=False,
                             is_html=False):
    # The basic strategy here is to build the template up to it's full
    # included/extended size, then work on the minimizing or precomputing
    # content from there.  That makes it multi-pass, but it avoids having a
    # dependency order.
    # If anything fails, just return the original template.  Worse case is
    # django's default behavior.
    if seen_templates is None:
        seen_templates = {}
    original_content = content

    processors = get_processors()

    for processor in processors:
        try:
            method = processor["method"]
            only_html = processor["html_only"]

            if only_html and not is_html:
                continue
            content = method(content,
                             seen_templates=seen_templates,
                             template_processor=process_sub_template,
                             )
        except Exception as ex:
            # We want to return the original template content if there are any
            # errors.  if we're processing an include/extended template, we
            # need to kick it back another level
            if subcall:
                raise
            return original_content

    return content


def get_default_config():
    return [
            {"method": "template_preprocess.process.extends.handle_extends"},
            {"method": "template_preprocess.process.includes.handle_includes"},
            {"method": "template_preprocess.process.compress_statics.process",
             "html_only": True
             },
            {"method": "template_preprocess.process.html_minify.process",
             "html_only": True
             },
            {"method": "template_preprocess.process.static.handle_static_tag",
             "html_only": True
             },
            # minify won't minify content in <script> tags, so this needs
            # to be the last thing done
            {"method": "template_preprocess.process.handlebars.process"},
            ]


def get_processors():
    config = getattr(settings,
                     "TEMPLATE_PREPROCESS_PROCESSORS",
                     get_default_config())

    processors = []
    for value in config:
        name = value["method"]
        module, attr = name.rsplit('.', 1)
        try:
            mod = import_module(module)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                       (module, str(e)))
        try:
            method = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a '
                                       '"%s" method' % (module, attr))

        processor = {"method": method, "html_only": False}

        if "html_only" in value and value["html_only"]:
            processor["html_only"] = True

        processors.append(processor)

    return processors
