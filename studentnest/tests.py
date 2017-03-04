from django.test import TestCase
from django.test import Client
from studentnest.models import *
from django.test.client import RequestFactory
import datetime

class StudentNestTest(TestCase):
    # Create your tests here.
    def setUp(self):
        super(StudentNestTest, self).setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.client = Client()
        self.user = User.objects.create_user(username="wenhoul1@andrew.cmu.edu", first_name="wenhou", last_name="lu",
                                             password="123", email="wenhoul1@andrew.cmu.edu")
        self.user.is_active = True
        self.assertIsNotNone(self.user)
        self.user.save()
        self.client.login(username="wenhoul1@andrew.cmu.edu", password="123")

        new_property = Property(name='amberson',
                                price='1231',
                                type='house',
                                min_bedroom_num='2',
                                max_bedroom_num='6',
                                description='description',
                                latitude='40.4537',
                                longitude='-79.9432',
                                street='Centre Ave',
                                city='Pittsburgh',
                                state='PA',
                                zip='15213',
                                contact_person='sarah',
                                contact_email='yupinh@andrew.cmu.edu',
                                contact_phone='123456789',
                                publisher=self.user)
        new_property.save()
        self.property = new_property

    def test_get_details_success(self):
        client = Client()
        response = client.get('/studentnest/details/1')
        self.assertTrue(response.status_code, 200)

    def test_get_details_fail(self):
        client = Client()
        response = client.get('/studentnest/details/2')
        self.assertTrue(response.status_code, 404)

    def test_change_password_success(self):
        client = Client()
        self.request.user = self.user
        response = client.post('/studentnest/change-password', {'original_password':'123',
                                                               'new_password1':'1234',
                                                               'new_password2':'1234'},)
        self.assertTrue(response.status_code, 200)

    def test_home_page(self):
        client = Client()
        response = client.get('/studentnest/')
        self.assertEqual(response.status_code, 200)

    def test_search_property(self):
        client = Client()
        response = client.get('''/studentnest/search-property?location=Pittsburgh&property_type=all
                &min_bedroom_num=0&max_bedroom_num=65535&min_price=-1&max_price=102400&action=search''')
        self.assertTrue(response.status_code, 200)

    def test_search_property_invalid(self):
        client = Client()
        response = client.get('/studentnest/search-property?parameter=invalid')
        self.assertTrue(response.status_code, 302)

    def test_register(self):
        client = Client()

        username = "yupinh@andrew.cmu.edu"
        password1 = "123"
        first_name = "yupin"
        last_name = "huang"

        university = "carnegie mellon unviersity"
        major = "art"
        response = client.post('/studentnest/register/',
                               {'username': username, 'password1': password1, 'first_name': first_name,
                                'last_name': last_name, 'email': username, 'university': university, 'major': major})
        self.assertTrue(response.status_code, 200)

    def test_login(self):
        client = Client()

        username = "yupinh@andrew.cmu.edu"
        password = "123"
        response = client.post('/studentnest/login/', {'username': username, 'password': password})
        self.assertTrue(response.status_code, 200)

    def test_reset_password(self):
        client = Client()

        username = "wenhoul1@andrew.cmu.edu"
        response = client.post('/studentnest/reset_password', {'username': username})
        self.assertTrue(response.status_code, 200)

class StudentNestModelsTest(TestCase):
    def test_user_add(self):
        self.assertTrue(User.objects.all().count() == 0)
        new_user = User(username='yupin',
                        password='password1',
                        email='yupinh@andrew.cmu.edu',
                        first_name='first_name',
                        last_name='last_name')
        new_user.save()
        self.assertTrue(User.objects.all().count() == 1)
        self.assertTrue(User.objects.filter(username__contains='yupin'))

    def test_property_add(self):
        self.assertTrue(Property.objects.all().count() == 0)
        new_user = User(username='yupin1',
                        password='password1',
                        email='yupinh@andrew.cmu.edu',
                        first_name='first_name',
                        last_name='last_name')
        new_user.save()

        new_property = Property(name='amberson',
                                price='1231',
                                type='house',
                                min_bedroom_num='2',
                                max_bedroom_num='6',
                                description='description',
                                latitude='40.4537',
                                longitude='-79.9432',
                                street='Centre Ave',
                                city='Pittsburgh',
                                state='PA',
                                zip='15213',
                                contact_person='sarah',
                                contact_email='yupinh@andrew.cmu.edu',
                                contact_phone='123456789',
                                publisher=new_user)

        new_property.save()

        self.assertTrue(Property.objects.all().count() == 1)
        self.assertTrue(Property.objects.filter(name__contains='amberson'))

    def test_property_keywords(self):
        self.assertTrue(PropertyKeywords.objects.all().count() == 0)
        new_user = User(username='yupin2',
                        password='password1',
                        email='yupinh@andrew.cmu.edu',
                        first_name='first_name',
                        last_name='last_name')
        new_user.save()
        new_property = Property(name='amberson',
                                price='1231',
                                type='house',
                                min_bedroom_num='2',
                                max_bedroom_num='6',
                                description='description',
                                latitude='40.4537',
                                longitude='-79.9432',
                                street='Centre Ave',
                                city='Pittsburgh',
                                state='PA',
                                zip='15213',
                                contact_person='sarah',
                                contact_email='yupinh@andrew.cmu.edu',
                                contact_phone='123456789',
                                publisher=new_user)
        new_property.save()

        new_propertykeywords = PropertyKeywords(property=new_property, keyword='clean', count=4)
        new_propertykeywords.save()

        self.assertTrue(PropertyKeywords.objects.all().count() == 1)
        self.assertTrue(PropertyKeywords.objects.filter(keyword__contains='clean'))

    def test_review(self):
        self.assertTrue(Review.objects.all().count() == 0)
        new_user = User(username='yupin3',
                        password='password1',
                        email='yupinh@andrew.cmu.edu',
                        first_name='first_name',
                        last_name='last_name')
        new_user.save()

        new_property = Property(name='amberson',
                                price='1231',
                                type='house',
                                min_bedroom_num='2',
                                max_bedroom_num='6',
                                description='description',
                                latitude='40.4537',
                                longitude='-79.9432',
                                street='Centre Ave',
                                city='Pittsburgh',
                                state='PA',
                                zip='15213',
                                contact_person='sarah',
                                contact_email='yupinh@andrew.cmu.edu',
                                contact_phone='123456789',
                                publisher=new_user)
        new_property.save()

        new_review = Review(
            author='sarah',
            rating='4.9',
            votes=0,
            content='ha',
            post_time=datetime.datetime.now(),
            property=new_property,
        )
        new_review.save()

        self.assertTrue(Review.objects.all().count() == 1)
        self.assertTrue(Review.objects.filter(rating__contains='4.9'))

    def test_review(self):
        self.assertTrue(Review.objects.all().count() == 0)
        new_user = User(username='yupin4',
                        password='password1',
                        email='yupinh@andrew.cmu.edu',
                        first_name='first_name',
                        last_name='last_name')
        new_user.save()
        new_property = Property(name='amberson',
                                price='1231',
                                type='house',
                                min_bedroom_num='2',
                                max_bedroom_num='6',
                                description='description',
                                latitude='40.4537',
                                longitude='-79.9432',
                                street='Centre Ave',
                                city='Pittsburgh',
                                state='PA',
                                zip='15213',
                                contact_person='sarah',
                                contact_email='yupinh@andrew.cmu.edu',
                                contact_phone='123456789',
                                publisher=new_user)
        new_property.save()

        new_review = Review(
            author=new_user,
            rating='4.9',
            votes=0,
            content='ha',
            post_time=datetime.datetime.now(),
            property=new_property,
        )
        new_review.save()

        self.assertTrue(Review.objects.all().count() == 1)
        self.assertTrue(Review.objects.filter(rating__contains='4.9'))

    def test_profile(self):
        self.assertTrue(Profile.objects.all().count() == 0)
        new_user = User(username='yupin5',
                        password='password1',
                        email='yupinh@andrew.cmu.edu',
                        first_name='first_name',
                        last_name='last_name')
        new_user.save()
        new_profile = Profile(user=new_user,
                              university='Carnegie Mellon University',
                              major='MIS')
        new_profile.save()
        self.assertTrue(Profile.objects.all().count() == 1)
        self.assertTrue(Profile.objects.filter(major__contains='MIS'))


