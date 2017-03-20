from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import TemplateView, FormView
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
import json
from .forms import RegisterForm, LoginForm, PhoneVerificationForm
from .authy_api import send_verfication_code, verify_sent_code
from .models import User

class IndexView(TemplateView):
    template_name = 'index.html'

class RegisterView(SuccessMessageMixin, FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_message = "One-Time password sent to your registered mobile number.\
                        The verification code is valid for 10 minutes."

    def form_valid(self, form):
        user = form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        try:
            response = send_verfication_code(user)
        except Exception as e:
            messages.add_message(self.request, messages.ERROR,
                                'verification code not sent. \n'
                                'Please re-register.')
            return redirect('/register')
        data = json.loads(response.text)

        print(response.status_code, response.reason)
        print(response.text)
        print(data['success'])
        if data['success'] == False:
            messages.add_message(self.request, messages.ERROR,
                            data['message'])
            return redirect('/dashboard')

        else:
            kwargs = {'user': user}
            self.request.method = 'GET'
            return PhoneVerificationView(self.request, **kwargs)

        # return super().form_valid(form)


def PhoneVerificationView(request, **kwargs):
    template_name = 'phone_confirm.html'

    if request.method == "POST":
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            verification_code = request.POST['one_time_password']
            user = User.objects.get(username=username)
            response = verify_sent_code(verification_code, user)
            print(response.text)
            data = json.loads(response.text)

            if data['success'] == True:
                login(request, user)
                if user.phone_number_verified is False:
                    user.phone_number_verified = True
                    user.save()
                return redirect('/dashboard')
            else:
                messages.add_message(request, messages.ERROR,
                                data['message'])
                return redirect('/login')

    elif request.method == "GET":
        user = kwargs['user']
        return render(request, template_name, {'user': user})

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = '/dashboard'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.add_message(self.request, messages.INFO,
                                "User already logged in")
            return redirect('/dashboard')
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.login(self.request)
        print(user.two_factor_auth)
        if user.two_factor_auth is False:
            login(self.request, user)
            return redirect('/dashboard')
        else:
            print("two factor")
            try:
                response = send_verfication_code(user)
                pass
            except Exception as e:
                messages.add_message(self.request, messages.ERROR,
                                    'verification code not sent. \n'
                                    'Please retry logging in.')
                return redirect('/login')
            data = json.loads(response.text)

            if data['success'] == False:
                messages.add_message(self.request, messages.ERROR,
                                data['message'])
                return redirect('/login')

            print(response.status_code, response.reason)
            print(response.text)
            if data['success'] == True:
                self.request.method = "GET"
                print(self.request.method)
                kwargs = {'user':user}
                return PhoneVerificationView(self.request, **kwargs)
            else:
                messages.add_message(self.request, messages.ERROR,
                        data['message'])
                return redirect('/login')


@method_decorator(login_required(login_url="/login/"), name='dispatch')
class DashboardView(SuccessMessageMixin, View):
    template_name = 'dashboard.html'

    def get(self, request):
        context = {
            'user':self.request.user,
            }
        if not request.user.phone_number_verified:
            messages.add_message(self.request, messages.INFO,
                                "User Not verified.")
        return render(self.request, self.template_name, context)

    def post(self, request):
        if 'two_factor_auth' in request.POST:
            if request.user.two_factor_auth:
                request.user.two_factor_auth = False
            else:
                request.user.two_factor_auth = True
            request.user.save()

        return render(self.request, self.template_name, {})
