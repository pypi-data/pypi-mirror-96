from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views import View
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, SuccessURLAllowedHostsMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import (
    is_safe_url, urlsafe_base64_decode,
)
from django_registration.backends.activation.views import RegistrationView
from djangoldp_account import settings

from djangoldp_account.endpoints.rp_login import RPLoginCallBackEndpoint, RPLoginEndpoint
from djangoldp_account.errors import LDPLoginError
from oidc_provider.views import userinfo


def userinfocustom(request, *args, **kwargs):
    if request.method == 'OPTIONS':
        response = HttpResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Authorization'
        response['Cache-Control'] = 'no-store'
        response['Pragma'] = 'no-cache'

        return response

    return userinfo(request, *args, **kwargs)


def check_user(request, *args, **kwargs):
    '''Returns user if they are authenticated with this server, else 404'''
    if request.method == 'OPTIONS':
        response = HttpResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Authorization'
        response['Cache-Control'] = 'no-store'
        response['Pragma'] = 'no-cache'

        return response

    if request.user.is_authenticated:
        response = JsonResponse(settings.userinfo({}, request.user))
        try:
            response['User'] = request.user.webid()
        except AttributeError:
            pass
        return response
    else :
        return HttpResponseNotFound()


# auxiliary function to set a user's default_redirect_uri
def _set_default_redirect_uri(user, redirect_uri):
    from django.conf import settings

    if redirect_uri is not None and len(redirect_uri) > 1 and redirect_uri != settings.LOGIN_REDIRECT_URL \
            and hasattr(user, 'default_redirect_uri'):
        try:
            user.default_redirect_uri = redirect_uri
            user.save()
        # if the URL is too long, or invalid, we can just move on
        except:
            pass


class RedirectView(View):
    """
    View for managing where to redirect the user after a successful login
    In the event that 'next' is not set (they may be coming from one of multiple front-end apps)

    To use this functionality set LOGIN_REDIRECT_URL to a url which uses this View. Then if the user
    has not set 'next' parameter in the login request, Django will redirect them here
    """
    def get(self, request, *args, **kwargs):
        from django.conf import settings

        if request.user.is_authenticated:
            next = request.user.default_redirect_uri

            # attempt to redirect to the user's default_redirect_uri
            if next is not None and len(next) > 1:
                return redirect(next, permanent=False)

        if getattr(settings, 'INSTANCE_DEFAULT_CLIENT', None) is not None:
            return redirect(settings.INSTANCE_DEFAULT_CLIENT, permanent=False)

        if getattr(settings, 'LOGIN_REDIRECT_DEFAULT', None) is not None:
            return redirect(settings.LOGIN_REDIRECT_DEFAULT, permanent=False)

        # there is no default to fall back on
        # redirect admins to the admin panel
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect(reverse('admin:index'), permanent=False)

        # redirect other users to a page apologising
        return render(request, template_name='registration/lost_user.html')


class LDPAccountLoginView(LoginView):
    """
    Extension of django.contrib.auth.views.LoginView for managing user's default_redirect_uri
    """
    def get_context_data(self, **kwargs):
        from django.conf import settings

        context = super().get_context_data(**kwargs)
        context.update({
            'registration_open': getattr(settings, 'REGISTRATION_OPEN', True),
            'distant_login': getattr(settings, 'DISTANT_LOGIN', False),
        })
        return context

    # Save login url as preferred redirect
    def post(self, request, *args, **kwargs):
        return_value = super(LDPAccountLoginView, self).post(request, *args, **kwargs)

        # if the user has 'next' set which is not default, update their preference
        next = request.POST.get('next')

        _set_default_redirect_uri(request.user, next)

        return return_value


class LDPAccountRegistrationView(SuccessURLAllowedHostsMixin, RegistrationView):
    """
    Extension of django-registration's RegistrationView for managing user's default_redirect_uri
    """
    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            'next',
            self.request.GET.get('next', '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'next': self.get_redirect_url(),
        })
        return context

    def post(self, request, *args, **kwargs):
        return_value = super(LDPAccountRegistrationView, self).post(request, *args, **kwargs)

        # if the user has 'next' set which is not default, update their preference
        next = request.POST.get('next', '')
        username = request.POST.get('username')

        # fetch the user which should now be created
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return return_value

        _set_default_redirect_uri(user, next)

        return return_value


class RPLoginView(View):
    """
    RP authentication workflow
    See https://github.com/solid/webid-oidc-spec/blob/master/example-workflow.md
    Wa're using oid module : https://pyoidc.readthedocs.io/en/latest/examples/rp.html
    """
    endpoint_class = RPLoginEndpoint

    def get(self, request, *args, **kwargs):
        return self.on_request(request)

    def on_request(self, request):
        endpoint = self.endpoint_class(request)
        try:
            endpoint.validate_params()

            return HttpResponseRedirect(endpoint.op_login_url())

        except LDPLoginError as error:
            return JsonResponse(error.create_dict(), status=400)

    def post(self, request, *args, **kwargs):
        return self.on_request(request)


# After a login request is made (on RPLoginEndpoint.op_login_url) the OP will redirect the user to this view
class RPLoginCallBackView(View):
    endpoint_class = RPLoginCallBackEndpoint

    def get(self, request, *args, **kwargs):
        return self.on_request(request)

    def on_request(self, request):
        endpoint = self.endpoint_class(request)
        try:
            endpoint.validate_params()

            return HttpResponseRedirect(endpoint.initial_url())

        except LDPLoginError as error:
            return JsonResponse(error.create_dict(), status=400)

    def post(self, request, *args, **kwargs):
        return self.on_request(request)
