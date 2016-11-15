import re
from template_preprocess.util.loader import Loader


def process_template_content(content, seen_templates={}, subcall=False):
    # The basic strategy here is to build the template up to it's full
    # included/extended size, then work on the minimizing or precomputing
    # content from there.  That makes it multi-pass, but it avoids having a
    # dependency order.
    # If anything fails, just return the original template.  Worse case is
    # django's default behavior.
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
            content = handle_compress(content)
            content = handle_minify(content)
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
    for match in re.finditer(block_regex, content, re.MULTILINE):
        block_name = match.group(1)
        full_block = match.group(0)
        block_values[block_name] = full_block

    # Now replace any blocks in the parent content with those blocks, and
    # return the parent content

    def replace_block(match):
        block_name = match.group(1)
        if block_name in block_values:
            return block_values[block_name]

        return match.group(0)

    content = re.sub(block_regex, replace_block, parent_content)
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
