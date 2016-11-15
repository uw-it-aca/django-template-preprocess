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

            source_path = templates[template]
            if template == "index.html":
                print "T: ", template, source_path, destination_path
