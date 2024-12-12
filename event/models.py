
import boto3
from django.db import models
from django.utils import timezone
from .aws_client import Registration

# Create your models here.

class RegistrationInfo(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    reg_date = models.DateTimeField(default=timezone.now)
    address = models.CharField(max_length=200)
    shirt_size = models.CharField(max_length=5)
    pick_up_event_day = models.BooleanField()


    def __str__(self):
        return self.first_name + " " + self.last_name


    def set_data(self, first_name, last_name, email, address, shirt_size, pick_up_event_day):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.address = address
        self.shirt_size = shirt_size

        if pick_up_event_day == None:
            self.pick_up_event_day = False
        else:
            self.pick_up_event_day = True


    def push_item_to_dynamodb(self, table_name):
        dyn_resource = boto3.resource("dynamodb")

        registration = Registration(dyn_resource)
        table_exists = registration.exists(table_name)

        if not table_exists:
            print(f"\nCreating {table_name} table...")
            registration.create_table(table_name)
            print(f"\nCreated table {registration.table.name}.")
        print(f"Adding item to the {table_name} table")

        registration.add_registration(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            reg_date=str(self.reg_date),
            address=self.address,
            shirt_size=self.shirt_size,
            pick_up_event_day=self.pick_up_event_day,
        )