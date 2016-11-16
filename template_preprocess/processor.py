from template_preprocess.util.loader import Loader
from django.template import Template, Context
import htmlmin
import re


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

    try:
        content = handle_extends_blocks(content, seen_templates)
        content = handle_includes(content, seen_templates)
    except Exception as ex:
        # We want to return the original template content if there are any
        # errors.  if we're processing an include/extended template, we need
        # to kick it back another level
        if subcall:
            raise
        else:
            return original_content

    if not subcall:
        try:
            if is_html:
                content = handle_statics_compress(content)
                content = handle_html_minify(content)
                content = handle_static_tag(content)
            # minify won't minify content in <script> tags, so this needs
            # to be the last thing done
            content = handle_handlebars(content)
        except Exception as ex:
            raise

    return content


def handle_extends_blocks(content, seen_templates={}):
    matches = re.search(r'{%\s*extends\s*"([^"]+)"\s*%}', content)
    if not matches:
        return content

    name = matches.group(1)

    if name in seen_templates:
        raise Exception("Recursive template in extends")

    seen_templates[name] = True

    parent_content = Loader().get_template_content(name)
    parent_content = process_template_content(parent_content,
                                              seen_templates,
                                              subcall=True)

    # Build a hash of block names to content, and then fill them in
    # in the parent template
    block_values = {}
    block_regex = r'{%\s*block\s+([^ ]+)\s*%}(.*?){%\s*endblock\s*\w*\s*%}'
    for match in re.finditer(block_regex, content, re.DOTALL):
        block_name = match.group(1)
        full_block = match.group(0)
        block_values[block_name] = full_block

    # We need to bring up any load tags that aren't in block content.
    # Start by getting all content that isn't in a block, then get the load
    # tags
    outside_of_blocks = re.sub(block_regex, "", content)
    load_tags = {}
    for match in re.finditer('{%\s*load\s+.*?%}', outside_of_blocks):
        load_tags[match.group(0)] = True

    # Now replace any blocks in the parent content with those blocks, and
    # return the parent content
    def replace_block(match):
        block_name = match.group(1)
        if block_name in block_values:
            return block_values[block_name]

        return match.group(0)

    content = re.sub(block_regex, replace_block, parent_content)

    # Now we add any loose load tags back in to the top of the page
    load_content = "".join(sorted(load_tags.keys()))
    return u"%s%s" % (load_content, content)


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

    content = re.sub(r"""{%\s*include\s*['"]([^"']+?)["']\s*%}""",
                     insert_template,
                     content, flags=re.UNICODE)

    return content


def handle_handlebars(content):
    def replace_handlebars(match):
        template_string = ("{% load templatetag_handlebars %}"
                           "{% load static %}"+match.group(0))
        t = Template(template_string)
        c = Context({})
        value = t.render(c)
        return "{% verbatim %}" + value + "{% endverbatim %}"

    regex = r'{%\s*tplhandlebars\s+[^\s]+\s*%}(.*?){%\s*endtplhandlebars\s*%}'
    content = re.sub(regex,
                     replace_handlebars,
                     content, flags=re.DOTALL)

    return content


def handle_static_tag(content):
    def replace_static_url(match):
        template_string = "{% load static %}"+match.group(0)
        print "TS: ", template_string
        t = Template(template_string)
        c = Context({})
        value = t.render(c)
        print "V: ", value
        return value

    content = re.sub(r'{%\s*static\s*[^%]+?%}',
                     replace_static_url,
                     content, flags=re.DOTALL)

    return content


def handle_statics_compress(content):
    def replace_compress_block(match):
        template_string = "{% load compress %}{% load static %}"+match.group(0)
        t = Template(template_string)
        c = Context({})
        value = t.render(c)
        return value

    content = re.sub(r'{%\s*compress\s+\w+\s*%}(.*?){%\s*endcompress\s*%}',
                     replace_compress_block,
                     content, flags=re.DOTALL)

    return content


def handle_html_minify(content):
    closing_blocks = []

    def sub_closing_handlebars(match):
        closing_blocks.append(match.group(0))

        return "{{__%s__}}" % (len(closing_blocks))
        print match.group(0)
        return match.group(0)

    def replace_closing_handlebars(match):
        return closing_blocks[int(match.group(1))-1]

    # handlebars templates get mangled by htmlmin.  but... we want them to be
    # minified, because in some apps that's most of the content.  this protects
    # the closing tag in at least one case where they'd be changed.
    content = re.sub(r'{{\s*/\s*\w+\s*}}', sub_closing_handlebars, content)

    minified = htmlmin.minify(content, remove_comments=True)

    # Put the closing tags back in
    content = re.sub(r'{{__(\d+)__}}', replace_closing_handlebars, minified)
    return content
