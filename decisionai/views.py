from django.shortcuts import render , redirect
from django.conf import settings
from django.views.decorators.cache import never_cache
from .open_ai import get_ai_decision
from django.http import JsonResponse
import json



@never_cache

def home(request):
    return render(request,"index.html")

def adduser(request):
    msg = ""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        coll = settings.DB["users"]
        
        existing_user = coll.find_one({"email": email})
        if existing_user:
            return render(request, "login.html", {
                "error": f"User with this email already exists."
            })
            
        dic = {
            "name": name,
            "email": email,
            "password": password
         
        }
        try:
            coll = settings.DB["users"]
            coll.insert_one(dic)
            msg = f"Registration successful. Please login."
        except:
            msg = "Registration failed"

    return render(request, "sign up.html", {"status": msg})

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        ps = request.POST.get("password")
        coll = settings.DB["users"]
        user = coll.find_one({"email": email, "password": ps})

        if user:
            request.session['authenticated'] = True
            request.session['email'] = user["email"]
            request.session['user'] = user.get("name", "User")  

          
            return redirect('/dashboard/')
        else:
            return render(request, "login.html", {
                "error": "Invalid email or password"
            })

    return render(request, "login.html")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        new_password = request.POST.get("password")

        coll = settings.DB["users"]

        user = coll.find_one({"email": email})

        if user:
            coll.update_one(
                {"email": email},
                {"$set": {"password": new_password}}
            )
            return render(request, "forgot pass.html", {
                "success": "Password updated successfully. Please login."
            })
        else:
            return render(request, "forgot pass.html", {
                "error": "Email not found"
            })

    return render(request, "forgot pass.html")

def dashboard(request):
    if not request.session.get('authenticated'):
        return redirect('/login/')
    username = request.session.get('user')
    return render(request, "dashboard.html",{"name":username})

def ai_decision(request):
    if not request.session.get("authenticated"):
        return JsonResponse({"result": "Unauthorized"}, status=401)

    if request.method == "POST":
        data = json.loads(request.body)
        user_text = data.get("problem")
        result = get_ai_decision(user_text)
        email = request.session.get("email")
        try:
            settings.DB["history"].insert_one({
                "email": email,
                "problem": user_text,
                "result": result
            })
        except Exception as e:
            print("DB insert failed:", e)

        return JsonResponse({"result": result})



def history(request):
    if not request.session.get("authenticated"):
        return redirect("/login/")

    email = request.session.get("email")

  
    records = list(settings.DB["history"].find(
        {"email": email},
        {"_id": 0}
    ).sort("problem", -1))

    return render(request, "history.html", {"records": records})








def profile(request):
    email = request.session.get('email')

    if not email:
        return redirect('/login/')

    user = settings.DB["users"].find_one({"email": email})

    return render(request, "profile.html", {"user": user})





def logout(request):
    request.session.flush()   
    return redirect('/')