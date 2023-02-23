from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from .models import EventDetails, SubscriptionDb
from django.forms import DateTimeField, DateTimeInput
from .forms import EventForm, AuthUserForm, RegisterUserForm
from .utils import send_emails

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q

from timestring import Date

# def index(request):
#     list_events = EventDetails.objects.all()

#     context = {
#         'list_events': list_events
#     }
#     template = 'index.html'

#     return render(request, template, context)
#     #return HttpResponse('<h1>Welcome</h1>')

class EventsListView(ListView):
    model = EventDetails
    template_name = 'index.html'
    context_object_name = 'list_events'
    def get(self, request, *args, **kwargs):
        if self.request.method == 'GET' and 'search' in request.GET:
            search_for = self.request.GET.get('search')
            if search_for != '':
                is_date = False
                try:
                    search_for_date = Date(search_for)
                    is_date = True
                except Exception:
                    pass

                if is_date and ('-' in search_for):
                    # date_list = search_for.split('-')
                    # self.queryset = EventDetails.objects.filter(
                    # time__year = date_list[0],
                    # time__month = date_list[1],
                    # time__day = date_list[2],
                    # )

                    self.queryset = EventDetails.objects.filter(
                    time__year = str(search_for_date.year),
                    time__month = str(search_for_date.month),
                    time__day = str(search_for_date.day),
                    )
                else:
                    self.queryset = EventDetails.objects.filter(
                    Q(title__icontains = search_for) |
                    Q(address__icontains = search_for) |
                    Q(description__icontains = search_for),)
        return super().get(self, request, *args, **kwargs)


# def manage_events(request):
#     if request.method == 'POST':
#         form = EventForm(request.POST)
#         if form.is_valid():
#             form.save()

#     context = {
#         'list_events': EventDetails.objects.all().order_by('-id'),
#         'form': EventForm()
#     }
#     template = 'manage_events.html'
#     return render(request, template, context)

class ManageEventsView(LoginRequiredMixin, CreateView):
    model = EventDetails
    template_name = 'manage_events.html'
    form_class = EventForm
    success_url = reverse_lazy('manage_events')

    # Different logic fot user groups: User and Attendant
    def get_context_data(self, **kwargs):
        if ('Attendant' in list(self.request.user.groups.values_list('name', flat = True))):
            kwargs['is_attendant'] = True
            attendant_id = self.request.user.id
            kwargs['booked_events'] = EventDetails.objects.filter(booked_by__id=attendant_id).all()
            kwargs['attend_events'] = EventDetails.objects.filter(attendants__id=attendant_id).all()
        else:
            #kwargs['list_events'] = EventDetails.objects.all().order_by('-id')
            #kwargs['list_events'] = EventDetails.objects.filter(author=self.request.user).values().order_by('-id')

            list_events = EventDetails.objects.filter(author=self.request.user).values().order_by('-id')
            kwargs['list_events'] = list_events
            kwargs['booked_by'] = dict()
            kwargs['attendants'] = dict()
            for ev in list_events:
                ev_id = ev['id']
                kwargs['booked_by'][ev_id] = EventDetails.objects.get(id=ev_id).booked_by.all()
                kwargs['attendants'][ev_id] = EventDetails.objects.get(id=ev_id).attendants.all()
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        if (self.request.GET.get('user') != None) and (self.request.GET.get('event') != None):
            self.object = None
            ev_id = self.request.GET.get('event')
            user_id = self.request.GET.get('user')
            EventDetails.objects.get(id=ev_id).attendants.add(User.objects.get(id=user_id))
            EventDetails.objects.get(id=ev_id).booked_by.remove(User.objects.get(id=user_id))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        author_user = User.objects.get(id=self.request.user.id)
        try:
            SubscriptionDb.objects.get(author=author_user)
        except SubscriptionDb.DoesNotExist:
            subs_info = SubscriptionDb(author=author_user)
            subs_info.save()

        send_emails(from_user=author_user, event=self.object)

        return super().form_valid(form)


# def edit_event(request, pk):
#     get_event = EventDetails.objects.get(pk=pk)

#     if request.method == 'POST':
#         form = EventForm(request.POST, instance = get_event)
#         if form.is_valid():
#             form.save()

#     context = {
#         'get_event': get_event,
#         'update': True,
#         'form': EventForm(instance = get_event),
#     }
#     template = 'edit_event.html'
#     return render(request, template, context)

class EditEventView(LoginRequiredMixin, UpdateView):
    model = EventDetails
    template_name = 'edit_event.html'
    form_class = EventForm
    success_url = reverse_lazy('manage_events')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if (kwargs['instance'].author != self.request.user):
            return self.handle_no_permission()
        return kwargs


# def delete_event(request, pk):
#     get_event = EventDetails.objects.get(pk=pk)
#     get_event.delete()
#     return redirect(reverse(manage_events))

class DeleteEventView(LoginRequiredMixin, DeleteView):
    model = EventDetails
    template_name = 'manage_events.html'
    success_url = reverse_lazy('manage_events')
    success_msg = "Event deleted"

    def post(self, request, *args, **kwargs):
        messages.success(self.request, self.success_msg)
        return super().post(request)

    def form_valid(self, form):
        success_url = self.get_success_url()
        if (self.request.user != self.object.author):
            return self.handle_no_permission()

        self.object.delete()
        return HttpResponseRedirect(success_url)

    # def delete(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     if (self.request.user != self.object.author):
    #         return self.handle_no_permission()
    #     success_url = self.get_success_url()
    #     self.object.delete()
    #     return HttpResponseRedirect(success_url)


class UserLogInView(LoginView):
    template_name = 'login.html'
    form_class = AuthUserForm
    success_url = reverse_lazy('manage_events')
    def get_success_url(self):
        return self.success_url

class UserLogOutView(LogoutView):
    next_page = reverse_lazy('index')

class RegisterUserView(CreateView):
    model = User
    template_name = 'register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('manage_events')

    # def form_valid(self, form):
    #     form_valid = super().form_valid(form)
    #     username = form.cleaned_data["username"]
    #     password = form.cleaned_data["password"]
    #     auth_user = authenticate(username = username, password = password)
    #     login(self.request, auth_user)
    #     return form_valid

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        if self.request.GET.get('type') == 'attendant':
            self.object = form.save(commit=False)
            attendant_group, _ = Group.objects.get_or_create(name='Attendant')
            self.object.groups.add(attendant_group)
            self.object.save()

        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        auth_user = authenticate(username = username, password = password)
        login(self.request, auth_user)
        return form_valid


class EditProfiletView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'my_profile.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('manage_events')

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        auth_user = authenticate(username = username, password = password)
        login(self.request, auth_user)
        return form_valid

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if (str(kwargs['instance'].username) != str(self.request.user)):
            return self.handle_no_permission()
        return kwargs


# def my_profile(request):
#     context = {
#     }
#     template = 'my_profile.html'
#     return render(request, template, context)


def book_event(request, id):
    if request.user.is_authenticated:
        EventDetails.objects.get(id=id).booked_by.add(User.objects.get(id=request.user.id))
        return redirect("manage_events")
    else:
        return redirect("login_page")

    
def subscribe_to_org(request, id):
    if request.user.is_authenticated:
        event = EventDetails.objects.get(id=id)
        user = User.objects.get(id=request.user.id)
        author = User.objects.get(id=event.author.id)
        SubscriptionDb.objects.get(author=author).subscribed_by.add(user) 
        # subs_users = SubscriptionDb.objects.get(author=author).subscribed_by.all()
        
        # for subs_user in subs_users:
        #     print(subs_user.username)

        context = {}
        template = 'subscribed.html'
        return render(request, template, context)
    else:
        return redirect("login_page")
