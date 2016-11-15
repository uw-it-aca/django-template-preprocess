from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os

from template_preprocess.util.loader import get_templates
from template_preprocess.processor import process_template_content


class Command(BaseCommand):
    def handle(self, *args, **options):
        templates = get_templates()
        for template in templates:
            destination_path = os.path.join(settings.COMPILED_TEMPLATE_PATH,
                                            template)

            try:
                os.makedirs(os.path.dirname(destination_path))
            except OSError:
                pass

            if template == "index.html":
                source_path = templates[template]
                with open(source_path) as source_handle:
                    content = source_handle.read()
                    content = process_template_content(content)

                    with open(destination_path, "w") as destination_handle:
                        destination_handle.write(content)
                print ("T: ", template, source_path, destination_path)
