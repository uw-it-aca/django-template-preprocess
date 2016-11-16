import re
import htmlmin


def process(content, seen_templates, template_processor):
    closing_blocks = []

    def sub_closing_handlebars(match):
        closing_blocks.append(match.group(0))

        return "{{__%s__}}" % (len(closing_blocks))

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
