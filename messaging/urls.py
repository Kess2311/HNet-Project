from django.conf.urls import url
from . import views

app_name = 'messaging'
urlpatterns = [
    url(r'^send/$', views.send_message, name='send')
]