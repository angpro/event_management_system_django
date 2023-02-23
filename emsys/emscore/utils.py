
from .models import EventDetails, SubscriptionDb
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.mail import EmailMessage, get_connection
from django.conf import settings


def send_emails(from_user: User, event: EventDetails):
    subs_users_emails = SubscriptionDb.objects.get(author=from_user).subscribed_by.values_list("email", flat=True)
    email_title = 'New event: ' + event.title
    email_body = 'Check new event!'

    # Google blocks sign-in attempts from apps which do not use modern security standards

    # with get_connection(  
    #         host=settings.EMAIL_HOST, 
    #         port=settings.EMAIL_PORT,  
    #         username=settings.EMAIL_HOST_USER, 
    #         password=settings.EMAIL_HOST_PASSWORD, 
    #         use_tls=settings.EMAIL_USE_TLS  
    #         ) as connection:  
    #             subject = email_title  
    #             email_from = settings.EMAIL_HOST_USER  
    #             recipient_list = list(subs_users_emails) 
    #             message = email_body
    #             EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()  
