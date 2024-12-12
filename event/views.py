from django.shortcuts import render
from django.contrib import messages
from .models import RegistrationInfo

# Create your views here.

def register(request):
    states = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
        "Wisconsin", "Wyoming"
    ]

    if request.method == "POST":
        first_name = request.POST.get("first-name")
        last_name = request.POST.get("last-name")
        email = request.POST.get("email")

        address = request.POST.get("street") + " "
        address += request.POST.get("unit").strip() + ", "
        address += request.POST.get("city") + ", "
        address += request.POST.get("state") + ", "
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