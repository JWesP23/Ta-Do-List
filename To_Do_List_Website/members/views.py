from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect



# Login
def login_func(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None: #Credentials correct
            login(request, user)  # logs the user in
            return redirect("home_page")  # redirect after login

        else: #Credentials incorrect
            return render(request, "registration/login.html", {"error": "Invalid Credentials. Perhaps You Meant To Sign Up Instead?"})

    else: #request is GET
        return render(request, "registration/login.html")


# Logout
def logout_func(request):
    logout(request)
    return redirect("home_page")


# Signup
def signup_func(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        username_in_use = User.objects.filter(username=username).exists()
        email_in_use = User.objects.filter(email=email).exists()

        if not username_in_use:
            if not email_in_use: #Credentials not taken
                user = User.objects.create_user(username, email, password) #create new user
                login(request, user)  #log the user in
                return redirect("home_page")  #redirect after signup
            else: #email taken
                return render(request, "registration/signup.html", {"error": "There's Already An Account With That Email. Perhaps You Meant To Login Instead?"})
        else: #username
            return render(request, "registration/signup.html", {"error": "There's Already An Account With That Username. Please Create A Different Username."})

    else: #request is GET
        return render(request, "registration/signup.html")