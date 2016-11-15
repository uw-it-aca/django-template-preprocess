import re
from template_preprocess.util.loader import Loader


def process_template_content(content, seen_templates={}, subcall=False):
    # The basic strategy here is to build the template up to it's full
    # included/extended size, then work on the minimizing or precomputing
    # content from there.  That makes it multi-pass, but it avoids having a
    # dependency order.
    # If anything fails, just return the original template.  Worse case is
    # django's default behavior.

    try:
        content = handle_extends_blocks(content, seen_templates)
        content = handle_includes(content, seen_templates)
        content = handle_compress(content)
        content = handle_minify(content)
        return content
    except Exception:
        # We want to return the original template content if there are any
        # errors.  if we're processing an include/extended template, we need
        # to kick it back another level
        if subcall:
            raise
        else:
            return content


def handle_extends_blocks(content, seen_templates={}):
    return content


def handle_includes(content, seen_templates={}):
    def insert_template(match):
        name = match.group(1)

        if name in seen_templates:
            raise Exception("Recursive template includes")
        path = Loader().get_template_path(name)
        content = Loader().get_template_content(name)

        seen_templates[name] = True
        content = process_template_content(content,
                                           seen_templates,
                                           subcall=True)
        return content

    content = re.sub(r'{%\s*include\s*"([^"]+)"\s*%}',
                     insert_template,
                     content)
    return content


def handle_compress(content):
    return content


def handle_minify(content):
    return content
