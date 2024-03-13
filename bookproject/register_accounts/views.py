from django.shortcuts import render,redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .formers import SignupForm
class SignupView(CreateView):
    model=User
    form_class=SignupForm
    template_name='accounts/signup.html'
    success_url=reverse_lazy('index')