from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import codecs

from template_preprocess.util.loader import get_templates, Loader
from template_preprocess.util.content_type import filename_is_html
from template_preprocess.processor import process_template_content


class Command(BaseCommand):
    def handle(self, *args, **options):
        templates = get_templates()
        ldr = Loader()
        for template in templates:
            destination_path = os.path.join(settings.COMPILED_TEMPLATE_PATH,
                                            template)

            try:
                os.makedirs(os.path.dirname(destination_path))
            except OSError:
                pass

            if True or template == "index.html":
                content = ldr.get_template_content(template)
                is_html = filename_is_html(template)
                content = process_template_content(content,
                                                   is_html=is_html)

                with codecs.open(destination_path,
                                 mode="w",
                                 encoding='utf-8') as destination_handle:
                    destination_handle.write(content)
