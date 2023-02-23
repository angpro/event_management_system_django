from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.EventsListView.as_view(), name='index'),
    path('manage-events', views.ManageEventsView.as_view(), name='manage_events'),

    path('login', views.UserLogInView.as_view(), name='login_page'),
    path('logout', views.UserLogOutView.as_view(), name='logout_page'),
    path('register', views.RegisterUserView.as_view(), name='register_page'),
    #path('my-profile', views.my_profile, name='my_profile'),
    path('my-profile/<int:pk>', views.EditProfiletView.as_view(), name='my_profile'),

    path('edit-event/<int:pk>', views.EditEventView.as_view(), name='edit_event'),
    path('delete-event/<int:pk>', views.DeleteEventView.as_view(), name='delete_event'),
    path('book/<int:id>', views.book_event, name='book_event'),
    path('subscribe/<int:id>', views.subscribe_to_org, name='subscribe_to_org'),
]