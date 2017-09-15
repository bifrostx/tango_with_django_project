from datetime import datetime
from rango.forms import CategoryForm, PageForm, UserProfileForm, UserForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from registration.backends.simple.views import RegistrationView
from rango.bing_search import bing_search
from django.contrib.auth.models import User

from rango.models import Category, Page, UserProfile


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,
                    'pages': page_list}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context=context_dict)
    return response


def about(request):

    visitor_cookie_handler(request)
    context_dict = {'author': "Han Xin", 'visits': request.session['visits']}
    return render(request, 'rango/about.html', context=context_dict)

    
def show_category(request, category_name_slug):
    context_dict = {}
    query = None

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        
        context_dict['pages'] = pages
        context_dict['category'] = category
        
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['page'] = None

    if request.method == 'POST':
        print("xxxxxxxxxxxxx")
        query = request.POST['query'].strip()
        if query:
            context_dict['result_list'] = bing_search(query)
            context_dict['query'] = query
    
    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
            
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
        
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                print("ok")
                return redirect('rango:show_category', category_name_slug)
        else:
            print(form.errors)
            
    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


'''
def register(request):

    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/user_login.html', {})


@login_required
def user_logout(request):

    logout(request)
    return HttpResponseRedirect(reverse('index'))

'''


class MyRegistrationView(RegistrationView):

    def get_success_url(self, user):
        return '/rango/register_profile/'


@login_required
def restricted(request):

    return render(request, 'rango/restricted.html', {})


def visitor_cookie_handler(request):

    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                       '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).seconds > 5:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        # visits = 1
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


def get_server_side_cookie(request, cookie, default_val=None):

    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


'''
# out of date
def search(request):
    result_list = []
    query = None
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = bing_search(query)

    return render(request, 'rango/category.html', {'result_list': result_list, 'query': query})
'''


def track_url(request):
    url = "/rango/"
    page_id = None
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id = page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                print("get page error")

        return redirect(url)


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('rango:index')
    else:
        print(form.errors)

    context_dict = {'form': form}

    return render(request, 'rango/profile_registration.html', context_dict)


@login_required
def profile(request, username):

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('rango:index')

    user_profile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': user_profile.website, 'picture': user_profile.picture}
    )

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print("errors")
            print(form.errors)
    else:
        return render(request, 'rango/profile.html',
                      {'user_profile': user_profile, 'selecteduser': user, 'form': form})


@login_required
def list_profiles(request):
    user_profile_list = UserProfile.objects.all()
    return render(request, 'rango/list_profiles.html',
                  {'user_profile_list': user_profile_list})



