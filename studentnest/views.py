from django.shortcuts import render
from django.db.models import Count
from collections import defaultdict
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from studentnest.models import *
from studentnest.forms import *
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from studentnest.models import Property
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from mimetypes import guess_type
from django.template.defaulttags import register
from django.db import transaction

from studentnest.models import *
from studentnest.forms import *

import services
from studentnest.arrays import stopwords
from studentnest.services import *
import collections
from decimal import Decimal
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
import datetime

from django.forms import formset_factory
from django.template.defaultfilters import linebreaksbr


def home(request):
    context = {}
    return render(request, 'studentnest/home.html', context)


def reviews(request, propertyId):
    context = {}
    result = get_reviews(request, propertyId)
    reviewer_statistics = analyze_reviewers(Property.objects.get(pk=propertyId))
    context['review_detail'] = result
    context['reviewer_statistics'] = reviewer_statistics
    return render(request, 'studentnest/details.html', context)


class ReviewDetail(object):
    def __init__(self, property):
        self.property = property


def get_reviews(request, propertyId):
    query_property = get_object_or_404(Property, pk=propertyId)
    if request.method == 'GET':
        return ReviewDetail(query_property)


@transaction.atomic
def add_review(request, id):
    # form available in the request context dictionary.
    context = {}
    query_property = get_object_or_404(Property, pk=id)
    # store the review into db
    new_review = Review(
        author=request.user,
        rating=request.POST['reviewRate'],
        votes=0,
        content=request.POST['content'],
        post_time=datetime.datetime.now(),
        property=query_property,
    )
    new_review.save()

    count_rating = query_property.review_set.count() - 1
    current_rating = (query_property.rating * count_rating + Decimal(request.POST['reviewRate']))/(count_rating + 1)
    query_property.rating = current_rating
    query_property.save()

    # when 10 more reviews comes on, regenerate the keywords
    if Review.objects.filter(property=query_property).count() % 10 == 0:
        regenerate_keywords(id)

    context['review'] = new_review
    reviewer_statistics = analyze_reviewers(Property.objects.get(pk=id))
    context['reviewer_statistics'] = reviewer_statistics
    return render(request, 'studentnest/review.json', context, content_type='application/json')


def regenerate_keywords(id):
    query_property = Property.objects.get(pk=id)

    # fetch all the content from review
    all_content = []
    reviews = Review.objects.filter(property=query_property)
    for review in reviews:
        text = [word.lower() for word in review.content.split() if word.lower() not in stopwords]
        all_content.extend(text)
    top20keywords = collections.Counter(all_content).most_common(20)

    # delete the records before insert
    PropertyKeywords.objects.filter(property=query_property).delete()

    # insert the 20 keywords
    for each_item in top20keywords:
        item = PropertyKeywords(property=query_property, keyword=each_item[0], count=each_item[1])
        item.save()


def search_property(request):
    context = {}
    if request.method == 'GET' and 'location' in request.GET and 'property_type' in request.GET and 'min_bedroom_num' in request.GET and 'max_bedroom_num' in request.GET and 'min_price' in request.GET and 'max_price' in request.GET and 'action' in request.GET \
            and request.GET['location'] and request.GET['property_type'] and request.GET['min_bedroom_num'] and \
            request.GET['max_bedroom_num'] and request.GET['min_price'] and request.GET['max_price'] and request.GET[
        'action']:
        location = request.GET['location']
        property_type = request.GET['property_type']
        min_bedroom_num = request.GET['min_bedroom_num']
        max_bedroom_num = request.GET['max_bedroom_num']
        min_price = request.GET['min_price']
        max_price = request.GET['max_price']
        action = request.GET['action']
        properties = []
        if property_type == 'all':
            properties = Property.objects.filter(Q(state__icontains=location) | Q(city__icontains=location),
                                                 Q(min_bedroom_num__gte=min_bedroom_num),
                                                 Q(max_bedroom_num__lte=max_bedroom_num), Q(price__gte=min_price),
                                                 Q(price__lte=max_price))
        else:
            properties = Property.objects.filter(Q(state__icontains=location) | Q(city__icontains=location),
                                                 Q(type=property_type), Q(min_bedroom_num__gte=min_bedroom_num),
                                                 Q(max_bedroom_num__lte=max_bedroom_num), Q(price__gte=min_price),
                                                 Q(price__lte=max_price))
        context['properties'] = properties
        if action == 'ajax_search':
            return render(request, 'studentnest/properties.json', context, content_type='application/json')
        elif action == 'search':
            return render(request, 'studentnest/list-property.html', context)
    return redirect(reverse('studentnest:home'))


def get_photo(request, id):
    query_property = Property.objects.get(pk=id)
    image = PropertyImage.objects.filter(property=query_property)[0]
    if not image:
        raise Http404
    content_type = guess_type(image.property_image.name)
    return HttpResponse(image.property_image, content_type)

def get_last1_photo(request, id):
    query_property = Property.objects.get(pk=id)
    image = PropertyImage.objects.filter(property=query_property).order_by("-upload_time")[0]
    if not image:
        raise Http404
    content_type = guess_type(image.property_image.name)
    return HttpResponse(image.property_image, content_type)

def get_last2_photo(request, id):
    query_property = Property.objects.get(pk=id)
    image = PropertyImage.objects.filter(property=query_property).order_by("-upload_time")[1]
    if not image:
        raise Http404
    content_type = guess_type(image.property_image.name)
    return HttpResponse(image.property_image, content_type)

def get_last3_photo(request, id):
    query_property = Property.objects.get(pk=id)
    image = PropertyImage.objects.filter(property=query_property).order_by("-upload_time")[2]
    if not image:
        raise Http404
    content_type = guess_type(image.property_image.name)
    return HttpResponse(image.property_image, content_type)


def login(request):
    if request.user.is_authenticated:
        return redirect(reverse('studentnest:home'))
    context = {}
    if request.method == 'GET':
        context['LoginForm'] = LoginForm()
        return render(request, 'studentnest/login.html', context)

    form = LoginForm(request.POST)

    context['LoginForm'] = form

    if not form.is_valid():
        return render(request, 'studentnest/login.html', context)

    user = authenticate(username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'])
    auth_login(request, user)
    return redirect(reverse('studentnest:home'))


def logout_view(request):
    logout(request)
    return redirect(reverse('studentnest:home'))


@transaction.atomic
def register(request):
    context = {}
    if request.method == 'GET':
        context['RegistrationForm'] = RegistrationForm()
        return render(request, 'studentnest/register.html', context)

    form = RegistrationForm(request.POST)
    context['RegistrationForm'] = form

    if not form.is_valid():
        return render(request, 'studentnest/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['username'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.is_active = False
    new_user.save()

    new_profile = Profile(user=new_user,
                          university=form.cleaned_data['university'],
                          major=form.cleaned_data['major'])
    new_profile.save()

    token = default_token_generator.make_token(new_user)
    email_body = """
     Welcome to StudentNest. Please click the link below to verify your emaill address and complete the registration of your account:

	http://%s%s
     """ % (request.get_host(), reverse('studentnest:confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="weijunw@andrew.cmu.edu",
              recipient_list=[new_user.email])
    context['email'] = new_user.email
    return render(request, 'studentnest/needs-confirmation.html', context)


@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username__exact=username)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
    return redirect(reverse('studentnest:login'))

@transaction.atomic
def apply_publish(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        profile = get_object_or_404(Profile, user=user)
        if not profile.is_publisher:
            now = datetime.datetime.now()
            difference = now - profile.last_applied.replace(tzinfo=None)
            if difference > datetime.timedelta(days=7):
                profile.last_applied = now
                profile.save()
                token = default_token_generator.make_token(user)
                email_body = """
     Got a new application for a publisher from user:
	username:%s
	lastname:%s
	firstname:%s
	gender:%s
	age:%s
	univsersity:%s
	major:%s

     If approve, please confirm by clicking the following link:

	http://%s%s
     """ % (user.username, user.last_name, user.first_name, profile.gender, profile.age, profile.university,
            profile.major, request.get_host(), reverse('studentnest:grant', args=(user.username, token)))

                send_mail(subject="Application for property publisher",
                          message=email_body,
                          from_email=user.email,
                          recipient_list=["weijunw@andrew.cmu.edu"])
                message = "Applied for a publisher! Please allow for up to seven days to process your application."
            else:
                message = "Sorry. You cannot send another application within seven days from your last application."
        else:
            message = "You are already an authorized Publisher."
    else:
	message = "Please login first."
    context['apply_message'] = message
    return render(request, 'studentnest/home.html', context)


def grant_publish(request, username, token):
    context = {}
    grant_user = get_object_or_404(User, username__exact=username)
    if default_token_generator.check_token(grant_user, token):
        profile = get_object_or_404(Profile, user=grant_user)
        profile.is_publisher = True
        profile.save()
    return redirect(reverse('studentnest:home'))

@transaction.atomic
def publish_property(request):
    if not request.user.is_authenticated:
        return redirect(reverse('studentnest:home'))
    profile = get_object_or_404(Profile, user=request.user)
    if not profile.is_publisher:
        return redirect(reverse('studentnest:home'))
    context = {}
    context['type'] = "publish"
    ImageFormSet = formset_factory(ImageForm, extra=3)
    if request.method == 'GET':
        context['PublishForm'] = PublishForm()
        context['FormSet'] = ImageFormSet()
        return render(request, 'studentnest/publish.html', context)

    form = PublishForm(request.POST)
    formset = ImageFormSet(request.POST, request.FILES)

    context['PublishForm'] = form
    if not form.is_valid() or not formset.is_valid():
        context['FormSet'] = ImageFormSet()
        return render(request, 'studentnest/publish.html', context)
    street = form.cleaned_data['street']
    city = form.cleaned_data['city']
    state = form.cleaned_data['state']
    coordinates = get_coordinates(street, city, state)
    if not coordinates is None:
        new_property = Property(name=form.cleaned_data['name'],
                                price=form.cleaned_data['price'],
                                type=form.cleaned_data['type'],
                                min_bedroom_num=form.cleaned_data['min_bedroom_num'],
                                max_bedroom_num=form.cleaned_data['max_bedroom_num'],
                                description=form.cleaned_data['description'],
                                latitude=coordinates['latitude'],
                                longitude=coordinates['longitude'],
                                street=form.cleaned_data['street'],
                                city=form.cleaned_data['city'],
                                state=form.cleaned_data['state'],
                                zip=form.cleaned_data['zip'],
                                contact_person=form.cleaned_data['contact_person'],
                                contact_email=form.cleaned_data['contact_email'],
                                contact_phone=form.cleaned_data['contact_phone'],
				publisher=request.user)
        new_property.save()
        for image_form in formset.cleaned_data:
            if image_form:
                image = image_form['property_image']
                new_image = PropertyImage(property=new_property, property_image=image)
                new_image.save()
        context['success'] = "Successfully published!"
    else:
        context['message'] = "Invalid address."
        context['FormSet'] = ImageFormSet()
        return render(request, 'studentnest/publish.html', context)

    return render(request, 'studentnest/home.html', context)


def manage_publish(request):
    if not request.user.is_authenticated:
        return redirect(reverse('studentnest:home'))
    profile = get_object_or_404(Profile, user=request.user)
    if not profile.is_publisher:
        return redirect(reverse('studentnest:home'))
    context = {}
    properties = Property.objects.filter(publisher=request.user)
    context['properties'] = properties
    return render(request, 'studentnest/manage.html', context)

@transaction.atomic
def edit_property(request,id):
    if not request.user.is_authenticated:
        return redirect(reverse('studentnest:home'))
    profile = get_object_or_404(Profile, user=request.user)
    if not profile.is_publisher:
        return redirect(reverse('studentnest:home'))
    property_to_edit = get_object_or_404(Property, pk=id)
    if property_to_edit.publisher!=request.user:
	return redirect(reverse('studentnest:home'))
    context = {}
    context['type'] = "edit_property"
    context['id'] = id
    ImageFormSet = formset_factory(ImageForm, extra=3)
    if request.method == 'GET':
        context['PublishForm'] = PublishForm(instance=property_to_edit)
        context['FormSet'] = ImageFormSet()
        return render(request, 'studentnest/publish.html', context)

    form = PublishForm(request.POST)
    formset = ImageFormSet(request.POST, request.FILES)

    context['PublishForm'] = form
    if not form.is_valid() or not formset.is_valid():
        context['FormSet'] = ImageFormSet()
        return render(request, 'studentnest/publish.html', context)
    street = form.cleaned_data['street']
    city = form.cleaned_data['city']
    state = form.cleaned_data['state']
    coordinates = get_coordinates(street, city, state)
    if not coordinates is None:
        property_to_edit.name=form.cleaned_data['name']
        property_to_edit.price=form.cleaned_data['price']
        property_to_edit.type=form.cleaned_data['type']
        property_to_edit.min_bedroom_num=form.cleaned_data['min_bedroom_num']
        property_to_edit.max_bedroom_num=form.cleaned_data['max_bedroom_num']
        property_to_edit.description=form.cleaned_data['description']
        property_to_edit.latitude=coordinates['latitude']
        property_to_edit.ongitude=coordinates['longitude']
        property_to_edit.street=form.cleaned_data['street']
        property_to_edit.city=form.cleaned_data['city']
        property_to_edit.state=form.cleaned_data['state']
        property_to_edit.zip=form.cleaned_data['zip']
        property_to_edit.contact_person=form.cleaned_data['contact_person']
        property_to_edit.contact_email=form.cleaned_data['contact_email']
        property_to_edit.contact_phone=form.cleaned_data['contact_phone']
        property_to_edit.save()
        for image_form in formset.cleaned_data:
            if image_form:
                image = image_form['property_image']
                new_image = PropertyImage(property=property_to_edit,property_image=image,upload_time=datetime.datetime.now())
                new_image.save()
        properties = Property.objects.filter(publisher=request.user)
        context['properties'] = properties
        context['success'] = "Successfully editted!"
    else:
        context['message'] = "Invalid address."
        context['FormSet'] = ImageFormSet()
        return render(request, 'studentnest/publish.html', context)

    return render(request, 'studentnest/manage.html', context)



def get_profile_image(request, profile_id):
    profile = get_object_or_404(Profile, pk=profile_id)

    if not profile.profile_images:
        raise Http404

    content_type = guess_type(profile.profile_images.name)
    print(content_type)
    return HttpResponse(profile.profile_images, content_type=content_type)


@transaction.atomic
def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect(reverse('studentnest:home'))
        
    context = {}

    profile_to_edit = get_object_or_404(Profile, user=request.user)
    context['profile_id'] = profile_to_edit.pk

    if request.method == 'GET':
        context['profile_form'] = ProfileForm(instance=profile_to_edit)
        return render(request, 'studentnest/edit-profile.html', context)

    form = ProfileForm(request.POST, request.FILES, instance=profile_to_edit)
    context['profile_form'] = form

    if not form.is_valid():
        return render(request, 'studentnest/edit-profile.html', context)

    print(form.cleaned_data['profile_images'])

    form.save()

    context['success_msg'] = 'You have successfully updated your profile.'
    return render(request, 'studentnest/edit-profile.html', context)


@transaction.atomic
def change_password(request):
    if not request.user.is_authenticated:
        return redirect(reverse('studentnest:home'))

    context = {}

    if request.method == 'GET':
        context['change_password_form'] = ChangePasswordForm()
        return render(request, 'studentnest/change-password.html', context)

    form = ChangePasswordForm(request.POST)
    context['change_password_form'] = form

    user = request.user

    if not authenticate(username=user.username, password=form.data['original_password']):
        context['password_error'] = 'The original password is not correct'
        return render(request, 'studentnest/change-password.html', context)

    if not form.is_valid():
        return render(request, 'studentnest/change-password.html', context)

    user.set_password(form.cleaned_data['new_password1'])
    user.save()

    authenticate(username=user.username, password=user.password)
    auth_login(request, user)

    context['success_msg'] = 'You have successfully changed your password.'
    return render(request, 'studentnest/change-password.html', context)


class ReviewerStatistics(object):
    def __init__(self, gender_statistics, age_statistics, univ_statistics, major_statistics):
        self.gender_statistics = gender_statistics
        self.age_statistics = age_statistics
        self.univ_statistics = univ_statistics
        self.major_statistics = major_statistics


class GenderStatistics(object):
    def __init__(self, male_count, female_count):
        self.male_count = male_count
        self.female_count = female_count


class AgeStatistics(object):
    def __init__(self, zero_seventeen_count, eighteen_twentytwo_count, twentythree_twentynine_count, thirty_more_count):
        self.zero_seventeen_count = zero_seventeen_count
        self.eighteen_twentytwo_count = eighteen_twentytwo_count
        self.twentythree_twentynine_count = twentythree_twentynine_count
        self.thirty_more_count = thirty_more_count


def analyze_reviewers(property):
    reviews = Review.objects.filter(property=property)
    reviewers_statistics = {}

    authors = []

    for review in reviews:
        authors.append(review.author)

    reviewers_profiles = Profile.objects.filter(user__in=authors)

    # statistics 1
    male_count = reviewers_profiles.filter(gender='M').count()
    female_count = reviewers_profiles.filter(gender='F').count()

    if male_count != 0 or female_count != 0:
        gender_statistics = GenderStatistics(male_count, female_count)
    else:
        gender_statistics = None

    # statistics 2
    zero_seventeen_count = reviewers_profiles.filter(age__gte=0, age__lte=17).count()
    eighteen_twentytwo_count = reviewers_profiles.filter(age__gte=18, age__lte=22).count()
    twentythree_twentynine_count = reviewers_profiles.filter(age__gte=23, age__lte=29).count()
    thirty_more_count = reviewers_profiles.filter(age__gte=30).count()

    if zero_seventeen_count != 0 or eighteen_twentytwo_count != 0 \
            or twentythree_twentynine_count != 0 or thirty_more_count:
        age_statistics = AgeStatistics(zero_seventeen_count, eighteen_twentytwo_count, twentythree_twentynine_count,
                                       thirty_more_count)
    else:
        age_statistics = None

    # statistics 3
    univ_statistics = reviewers_profiles.values('university').annotate(total=Count('university')).order_by('-total')[:5]

    if not univ_statistics:
        univ_statistics = None

    # statistics 4
    major_statistics = reviewers_profiles.values('major').annotate(total=Count('major')).order_by('-total')[:5]

    if not major_statistics:
        major_statistics = None

    return ReviewerStatistics(gender_statistics, age_statistics, univ_statistics, major_statistics)


@transaction.atomic
def incr_like(request, id):
    review = Review.objects.filter(id=id)[0]
    review.votes += 1
    review.save()
    return HttpResponse(status=200)


def reset_password(request):
    context = {}

    if request.method == 'GET':
        context['ResetForm'] = ResetForm()
        return render(request, 'studentnest/reset-password.html', context)

    form = ResetForm(request.POST)
    context['ResetForm'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'studentnest/reset-password.html', context)

    # If we get here the form data was valid.  Register and login the user.
    user = get_object_or_404(User,username=form.cleaned_data['username'])
    if not user.is_active:
	context['message'] = "Please activate your account first."
	return render(request, 'studentnest/reset-password.html', context)
    token = default_token_generator.make_token(user)
    email_body="""
     Welcome to StudentNest. Please click the link below to reset the password of your account:

	http://%s%s
     """ % (request.get_host(), reverse('studentnest:reset_confirm', args=(user.username, token)))

    send_mail(subject="Verify your email address",
		  message=email_body,
		  from_email="weijunw@andrew.cmu.edu",
		  recipient_list=[user.email])
    message = "An email has been sent to the address. Please confirm and then reset the password."
    context['message'] = message
    return render(request, 'studentnest/reset-password.html', context)

def reset_confirm(request, username, token):
    context = {}
    if not request.method == 'GET':
	return redirect(reverse('studentnest:login'))
    context['ResetConfirmForm'] = ResetConfirmForm()
    context['username'] = username
    return render(request, 'studentnest/reset-confirm.html', context)


def reset_success(request, username):
    context={}
    if request.method == 'GET':
	return redirect(reverse('studentnest:login'))
    form = ResetConfirmForm(request.POST)
    context['ResetConfirmForm'] = form
    context['username'] = username
    # Validates the form.
    if not form.is_valid():
        return render(request, 'studentnest/reset-confirm.html', context)
    # If we get here the form data was valid.  Reset the password.
    if User.objects.get(username=username):
	user = User.objects.get(username=username)
        user.set_password(form.cleaned_data['password1'])
        user.save()
    return redirect(reverse('studentnest:login'))
