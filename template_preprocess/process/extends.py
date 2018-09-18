import re


def handle_extends(content, seen_templates, template_processor):
    matches = re.search(r'{%\s*extends\s*"([^"]+)"\s*%}', content)
    if not matches:
        return content

    name = matches.group(1)

    if name in seen_templates:
        raise Exception("Recursive template in extends")

    seen_templates[name] = True

    parent_content = template_processor(name, seen_templates)
    # Build a hash of block names to content, and then fill them in
    # in the parent template
    block_values = {}
    block_regex = r'{%\s*block\s+([^ ]+)\s*%}(.*?){%\s*endblock\s*(\1|)\s*%}'
    for match in re.finditer(block_regex, content, re.DOTALL):
        block_name = match.group(1)
        full_block = match.group(0)
        block_values[block_name] = full_block

    # We need to bring up any load tags that aren't in block content.
    # Start by getting all content that isn't in a block, then get the load
    # tags
    outside_of_blocks = re.sub(block_regex, "", content)
    load_tags = {}
    for match in re.finditer(r'{%\s*load\s+.*?%}', outside_of_blocks):
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
