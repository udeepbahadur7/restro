import os
import shutil
import zipfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from wifiportal.models import Organization


FILE_EXPORT_DIRECTORY = os.path.join(settings.BASE_DIR, 'dist-mt/')
TEMPLATE_MT_DIR = os.path.join(settings.BASE_DIR, 'templates', 'mikrotikpages')
MIKROTIK_PAGES_EXPORT_DIR = os.path.join(FILE_EXPORT_DIRECTORY, 'mikrotikpages')
MIKROTIK_PAGES_ZIP_EXPORT_PATH = os.path.join(FILE_EXPORT_DIRECTORY, 'mt-hotspot-pages.zip')


def zipdir(path, outputFilePath):
    # ziph is zipfile handle
    zipf = zipfile.ZipFile(outputFilePath, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path, '..'))
            )
    zipf.close()


class Command(BaseCommand):
    help = "Generate Mikrotik Hotspot Pages. Please provide organization id"

    def add_arguments(self, parser):
        parser.add_argument('organization_id')

    def handle(self, *args, **options):
        self.print_log("Cleaning export path", options)
        self.clean_export_path()
        self.print_log('Making contexts', options)
        context = self.get_context(options)
        self.print_log('Copying Files', options)
        self.copy_files(context)
        zipdir(MIKROTIK_PAGES_EXPORT_DIR, MIKROTIK_PAGES_ZIP_EXPORT_PATH)
        self.print_log(self.style.SUCCESS('Done!!!'), options)
        self.print_log(self.style.SUCCESS('Files exported to ' + FILE_EXPORT_DIRECTORY), options)

    def clean_export_path(self):
        if not os.path.exists(FILE_EXPORT_DIRECTORY):
            os.makedirs(FILE_EXPORT_DIRECTORY)
        else:
            shutil.rmtree(FILE_EXPORT_DIRECTORY)
            os.makedirs(FILE_EXPORT_DIRECTORY)

    def get_context(self, options):
        organization_id = options.get('organization_id', None)
        if not organization_id:
            raise CommandError('Organization ID missing. ./manage.py createmtpages <organization_id>')

        try:
            organization = Organization.objects.get(pk=organization_id)
        except (Organization.DoesNotExist, ValidationError):
            raise CommandError('Organization({}) not found'.format(organization_id))

        hotspot_url = "http://infiniasmart.com/portal/client/{}/".format(organization_id)
        self.print_log(self.style.SUCCESS("Organization :: " + organization.name), options)

        return dict(
            organization=organization,
            hotspot_url=hotspot_url
        )

    def _create_sub_dirs(self):
        os.makedirs(MIKROTIK_PAGES_EXPORT_DIR)

    def copy_files(self, context):
        template_files = ['alogin.html', 'error.html', 'errors.txt',
                            'login.html', 'logout.html', 'radvert.html',
                            'redirect.html', 'rlogin.html', 'status.html']

        self._create_sub_dirs()
        self.copy_static_files()

        for template_file in template_files:
            template_file_path = 'mikrotikpages/'+ template_file
            template_string = render_to_string(template_file_path, context)

            output_file_path = os.path.join(MIKROTIK_PAGES_EXPORT_DIR, template_file)
            with open(output_file_path, 'w') as file_ptr:
                file_ptr.write(template_string)

    def copy_static_files(self):
        static_files = ['md5.js', 'favicon.ico']
        for static_file in static_files:
            static_file_path = os.path.join(TEMPLATE_MT_DIR, static_file)
            static_dest_file_path = os.path.join(FILE_EXPORT_DIRECTORY, 'mikrotikpages', static_file)
            shutil.copyfile(static_file_path, static_dest_file_path)

    def print_log(self, message, options):
        if options.get('verbosity', 1) != 0:
            self.stdout.write(message)



