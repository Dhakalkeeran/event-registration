from django.shortcuts import render
from django.contrib import messages
from .models import RegistrationInfo, states

# Create your views here.

def register(request):

    if request.method == "POST":
        first_name = request.POST.get("first-name")
        last_name = request.POST.get("last-name")
        email = request.POST.get("email")

        address = request.POST.get("street") + " "
        address += request.POST.get("unit").strip() + ", "
        address += request.POST.get("city") + ", "
        address += states[request.POST.get("state")] + ", "
        address += request.POST.get("postal-code")

        shirt_size = request.POST.get("size")
        pick_up = request.POST.get("pickup")

        reg_info = RegistrationInfo()
        reg_info.set_data(
            first_name=first_name, 
            last_name=last_name, 
            email=email, 
            address=address, 
            shirt_size=shirt_size, 
            pick_up_event_day=pick_up,
        )

        table_name = "RegistrationTable"
        reg_info.push_item_to_dynamodb(table_name)
        messages.success(request, f"Registration Successful for {first_name} {last_name}")

    return render(request, "event/register.html", context={"states": states})