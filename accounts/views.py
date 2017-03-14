from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import RegisterForm, LoginForm


class IndexView(FormView):
    template_name = 'index.html'
    form_class = RegisterForm
    success_url = '/dashboard'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        user = form.save()
        print(user)
        print(self.request)
        print(self.request.POST['username'])
        username = self.request.POST['username']
        password = self.request.POST['password1']
        print('username',username, password)

        user = authenticate(username=username, password=password)
        login(self.request, user)

        # return super(RegisterForm, self).form_valid(form)

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(username=username, password=password)
        print(user, username, password)
        if user is not None:
            login(self.request, user)
            return redirect('/dashboard')
        else:
            return redirect('/login')


@method_decorator(login_required(login_url="/"), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'
