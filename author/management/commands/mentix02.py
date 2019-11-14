from django.core.management.base import BaseCommand, CommandError

from author.models import Author


class Command(BaseCommand):

    help = 'A one time creation script for creating "mentix02" admin superuser.'

    def get_version(self):
        return '1.0.0'

    def handle(self, *args, **options):

        try:

            print('Creating author...', end=' ')
            Author.objects.create_superuser(
                password='aaa',
                first_name='Manan',
                username='mentix02',
                email='manan.yadav02@gmail.com'
            )
            print('done')

        except Exception as e:
            raise CommandError(str(e))
