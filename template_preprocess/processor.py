import re
from template_preprocess.util.loader import Loader
from slimmer import html_slimmer


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
            content = handle_handlebars(content)
            if is_html:
                content = handle_statics_compress(content)
                content = handle_html_minify(content)
        except Exception as ex:
            raise

    return content


def handle_extends_blocks(content, seen_templates={}):
    matches = re.search(r'{%\s*extends\s*"([^"]+)"\s*%}', content)
    if not matches:
        return content

    name = matches.group(1)

    if name in seen_templates:
        raise Exception("Recursive template in extends - %s" % (str(seen_templates) ))

    seen_templates[name] = True

    parent_content = Loader().get_template_content(name)
    parent_content = process_template_content(parent_content,
                                              seen_templates,
                                              subcall=True)

    # Build a hash of block names to content, and then fill them in
    # in the parent template
    block_values = {}
    block_regex = r'{%\s*block\s+([^ ]+)\s*%}(.*?){%\s*endblock\s*\w*\s*%}'
    for match in re.finditer(block_regex, content, re.MULTILINE):
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
    return "%s%s" % (load_content, content)


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
                     content)
    return content


def handle_handlebars(content):
    return content


def handle_statics_compress(content):
    return content


def handle_html_minify(content):
    return html_slimmer(content)
