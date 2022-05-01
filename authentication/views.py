from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from passmngt import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout

from .models import Password

from .forms import PasswordForm
from . tokens import generate_token
# from django.views.decorators.csrf import csrf_exempt

# Create your views here.   
# def home(request):
#     return render(request, "authentication/index.html")

def get_projects(request):
    data = request.POST
   
    if data:
        key = data.get('filter')
        user_passwords = {} if key is None else Password.objects.filter(title__contains=key)
    else:
        user_passwords = Password.objects.all().order_by('-date_created')
    return render(request, "index.html", {"user_passwords": user_passwords,})



    

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('view_all_projects')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('view_all_projects')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('view_all_projects')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('view_all_projects')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('view_all_projects')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        # myuser.is_active = False
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
        
        # Welcome Email
        subject = "Welcome to Fola's Password Management!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Fola's PM!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThank You\nAfolabi Sanni"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ Fola's PM!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
        
        
    return render(request, "signup.html")


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            # messages.success(request, "Logged In Sucessfully!!")
            return render(request, "index.html",{"fname":fname})
        else:
            messages.error(request, "Invalid login!! Please check your email to activate your account if registered")
            return redirect('view_all_projects')
    
    return render(request, "signin.html")

    



def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('view_all_projects')



def create_project(request):
    data = request.POST
    form = PasswordForm()
    if request.method == "POST":
        form = PasswordForm(data=data)
        website = data.get('website')
        if form.is_valid():
            form.save()
            form = PasswordForm()
            messages.success(request, f"{website}'s password just got created")
            return redirect('view_all_projects')
        
    return render(request, "create_project.html", {"form": form})



def filter_projects(request):
    data = request.POST
    key = data.get('filter')
    if key is not None:
        user_password = Password.objects.filter(title__contains=key)
    else:
        user_password = {}
    return render(request, "filtered_projects.html", {'user_password': user_password})

def retrieve_projects(request, id):
    if Password.objects.filter(id=id).exists():
        user_password = Password.objects.get(id=id)
    else:
        user_password = {}
    return render(request, 'project_detail.html', {'user_password': user_password})

def update_project(request, id):
    user_password = Password.objects.get(id=id)
    form = PasswordForm(instance=user_password)
    data = request.POST
    print(data)
    if request.method == "POST":
        form = PasswordForm(instance=user_password, data=data)
        if form.is_valid():
            form.save()
            print("here")
            return redirect('retrieve_projects', id)
                   
    return render(request, "update_project.html", {'user_password': user_password, 'form': form})


def delete_project(request, id):
    if Password.objects.filter(id=id).exists():
        Password.objects.get(id=id).delete()        
        print('Project successfully deleted')
    return redirect('view_all_projects')
