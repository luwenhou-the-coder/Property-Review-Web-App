from django.conf.urls import include, url
import studentnest.views

app_name = 'studentnest'

urlpatterns = [
    url(r'^$', studentnest.views.home, name='home'),
    url(r'^search-property$', studentnest.views.search_property, name='search_property'),
    url(r'^details/(?P<propertyId>.*)?$', studentnest.views.reviews, name='reviews'),
    url(r'^list-property$', studentnest.views.home, name='list_property'),
    url(r'^register/$', studentnest.views.register,name='register'),
    url(r'^login/$', studentnest.views.login,name='login'),
    url(r'^logout/$', studentnest.views.logout_view,name='logout'),
    url(r'^confirm/(?P<username>.*)/(?P<token>.*)$', studentnest.views.confirm_registration,name='confirm'),
    url(r'^photo/(?P<id>\d+)$',studentnest.views.get_photo,name='photo'),
    url(r'^photo1/(?P<id>\d+)$',studentnest.views.get_last1_photo,name='photo1'),
    url(r'^photo2/(?P<id>\d+)$',studentnest.views.get_last2_photo,name='photo2'),
    url(r'^photo3/(?P<id>\d+)$',studentnest.views.get_last3_photo,name='photo3'),
    url(r'^publish/$', studentnest.views.publish_property,name='publish'),
    url(r'^edit-profile$', studentnest.views.edit_profile, name='edit_profile'),
    url(r'^profile-images/(?P<profile_id>\d+)$', studentnest.views.get_profile_image, name="profile_image"),
    url(r'^change-password$', studentnest.views.change_password, name='change_password'),
    url(r'^incrLike/(?P<id>.*)$', studentnest.views.incr_like, name='incrLike'),
    url(r'^postReview/(?P<id>.*)$', studentnest.views.add_review, name='postReview'),
    url(r'^apply-publish/$', studentnest.views.apply_publish, name='apply_publish'),
    url(r'^grant/(?P<username>.*)/(?P<token>.*)$', studentnest.views.grant_publish, name='grant'),
    url(r'^manage/$', studentnest.views.manage_publish, name='manage'),
    url(r'^edit-property/(?P<id>\d+)$', studentnest.views.edit_property, name='edit_property'),
    url(r'^reset_password/$',studentnest.views.reset_password,name='reset_password'),
    url(r'^reset_confirm/(?P<username>.*)/(?P<token>.*)$', studentnest.views.reset_confirm,name='reset_confirm'),
    url(r'^reset_success/(?P<username>.*)$', studentnest.views.reset_success,name='reset_success'),
]