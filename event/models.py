
import boto3
import logging
import os
import smtplib

from django.db import models
from django.utils import timezone
from email.message import EmailMessage

from .aws_client import Registration

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

states = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

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
        
        self.email_content = "event/email_content.txt"


    def push_item_to_dynamodb(self, table_name):
        dyn_resource = boto3.resource("dynamodb")
        registration = Registration(dyn_resource)
        table_exists = registration.exists(table_name)

        if not table_exists:
            logger.info(f"\nCreating {table_name} table...")
            registration.create_table(table_name)
            logger.info(f"\nCreated table {registration.table.name}.")
        logger.info(f"Adding item to the {table_name} table")

        registration.add_registration(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            reg_date=str(self.reg_date),
            address=self.address,
            shirt_size=self.shirt_size,
            pick_up_event_day=self.pick_up_event_day,
        )

        try:
            logger.info(f"Sending email to {self.email}")
            self.send_email()
        except Exception as e:
            logger.error("Error occurred!", e)


    def send_email(self):
        with open(self.email_content) as fp:
            msg = EmailMessage()
            msg.set_content(f"Hi {self.first_name},\n\n" + fp.read())

        msg['Subject'] = "Event Registration Successful!"
        msg['From'] = os.environ["EMAIL"]
        msg['To'] = self.email

        # Send the message via our own SMTP server.
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.environ["EMAIL"], os.environ["PASSWORD"])

        server.send_message(msg)
        server.quit()
