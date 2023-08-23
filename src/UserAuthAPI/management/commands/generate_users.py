### Warning! This program can only be used for testing purpose ###
import datetime
import random
import string
from typing import List

# Get dependency: pip install names
import names
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from UserAuthAPI.models import User, UserProfile


def create_user():
    GENDER_RANGE: List[str] = ['Male', 'Female']
    PASSWORD_SAMPLE: str = 'test123456'
    DATE_ORIGIN: str = datetime.date(1993, 1, 1)

    gender: str = random.choice(GENDER_RANGE)
    name: str = names.get_full_name(gender=gender)

    def _email_gen(name: str):
        ENDFIX = '@gmail.com'
        random_chars = ''.join(random.choice(string.ascii_letters)
                               for i in range(0, 4))
        return name.replace(' ', '') + '_' + random_chars + ENDFIX

    def _telNumber_gen():
        PREFIX = '04'
        return PREFIX + ''.join(random.choice(string.digits) for i in range(0, 8))

    def _studentId_gen():
        return ''.join(random.choice(string.digits) for i in range(0, 6))

    def _membershipId_gen():
        # random.seed(72512)
        return ''.join(random.choice(string.digits) for i in range(0, 5))

    def _random_date_gen():
        return DATE_ORIGIN + datetime.timedelta(days=random.randint(0, 1000))

    new_user: User = User(
        email=_email_gen(name),
        telNumber=_telNumber_gen(),
        password=PASSWORD_SAMPLE,
    )
    new_user.save()

    new_user_profile: UserProfile = UserProfile(
        user=new_user,
        identiyConfirmed=True,
        isValid=True,
        firstNameEN=name.split(' ')[0],
        lastNameEN=name.split(' ')[1],
        gender=gender,
        dateOfBirth=_random_date_gen(),
        studentId=_studentId_gen(),
        membershipId=_membershipId_gen(),
    )
    new_user_profile.save()
    return name


class Command(BaseCommand):
    help = 'Adding test user data into the system database /n Warning! This command can only used in Development Mode'

    def add_arguments(self, parser):
        parser.add_argument('--num_of_users', nargs='?',
                            type=int, const=10, default=10)

    def handle(self, *args, **options):
        if settings.DEBUG is False:
            raise CommandError(
                'This command is forbidden to use in Production Mode')
        num_of_users = options['num_of_users']
        if num_of_users < 0:
            raise CommandError(
                'The number of users you want to create must larger than 0')

        for i in range(0, num_of_users):
            self.stdout.write(self.style.SUCCESS(
                (f"The {i+1} user is created, named {create_user()}")))
        return 0
