from django.test import TestCase

from author.models import Author


class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.mentix02: Author = Author.objects.create_user(
            first_name='Manan',
            password='abcd1432',
            username='mentix02',
            email='manan.yadav02@example.com',
            bio='I like to write so I wrote this site.',
        )

        cls.aryan: Author = Author.objects.create_user(
            first_name='Aryan',
            password='abcd1432',
            username='aryan123',
            email='aryan123@example.com',
            bio="I like to play football so I'm stuck here."
        )

    def test_author_a_verify_method(self):
        """
        Checks if Author's verify function works to convert its
        verified field status to True. The name has an _a_ in it
        because this test needs to run before the promotion test
        and the character 'v' comes after 'p' and Python runs its
        tests in alphabetical order so I had to insert an a in
        the center. It's an ungly hack but it works; don't change it.
        """

        # First confirm that is_staff and verified fields are False
        self.assertEqual(self.mentix02.verified, False)
        self.assertEqual(self.mentix02.is_staff, False)

        self.mentix02.verify()

        # Now the author should only be verified - not staff.
        self.assertEqual(self.mentix02.verified, True)
        self.assertEqual(self.mentix02.is_staff, False)

    def test_author_promote_method(self):
        """
        Checks the functioning of the promote method that not
        only verifies the Author but also makes it is_staff member.
        """

        # First confirm that is_staff and verified fields are False
        self.assertEqual(self.aryan.verified, False)
        self.assertEqual(self.aryan.is_staff, False)

        self.aryan.promote()

        # Now the author should be both verified and staff
        self.assertEqual(self.aryan.verified, True)
        self.assertEqual(self.aryan.is_staff, True)

        # Now test if with Author that was verified before
        # being promoted as that's going to be the norm mostly.

        self.assertEqual(self.mentix02.verified, True)
        self.assertEqual(self.mentix02.is_staff, False)

        self.mentix02.promote()

        self.assertEqual(self.mentix02.verified, True)
        self.assertEqual(self.mentix02.is_staff, True)
