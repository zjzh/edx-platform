"""
Management command `manage_user` is used to idempotently create or remove
Django users, set/unset permission bits, and associate groups by name.
"""


from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import is_password_usable, identify_hasher
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from edx_django_utils.admin.manage_users_by import update_user

from openedx.core.djangoapps.user_authn.utils import generate_password
from common.djangoapps.student.models import UserProfile


class Command(BaseCommand):  # lint-amnesty, pylint: disable=missing-class-docstring
    help = 'Creates the specified user, if it does not exist, and sets its groups.'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('email')
        parser.add_argument('--remove', dest='is_remove', action='store_true')
        parser.add_argument('--superuser', dest='is_superuser', action='store_true')
        parser.add_argument('--staff', dest='is_staff', action='store_true')
        parser.add_argument('--unusable-password', dest='unusable_password', action='store_true')
        parser.add_argument('--initial-password-hash', dest='initial_password_hash')
        parser.add_argument('-g', '--groups', nargs='*', default=[])

    @transaction.atomic
    def handle(
        self, username, email, is_remove, is_staff, is_superuser, groups, unusable_password,
        initial_password_hash, *args, **options):

        update_user(username, email, is_remove, is_staff, is_superuser, groups,unusable_password, initial_password_hash)
