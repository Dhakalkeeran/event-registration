import logging
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class Registration:

    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        # The table variable is set during the scenario in the call to
        # 'exists' if the table exists. Otherwise, it is set by 'create_table'.
        self.table = None

    def exists(self, table_name):
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.

        :param table_name: The name of the table to check.
        :return: True when the table exists; otherwise, False.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        else:
            self.table = table
        return exists

    def create_table(self, table_name):
        """
        Creates an Amazon DynamoDB table that can be used to store registration data.
        The table uses the email address of the registramt as the partition key and the
        registered date as the sort key.

        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "email", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "reg_date", "KeyType": "RANGE"},  # Sort key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "email", "AttributeType": "S"},
                    {"AttributeName": "reg_date", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
            )
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return self.table
        
    def add_registration(self, first_name, last_name, email, reg_date, address, shirt_size, pick_up_event_day):
        """
        Adds a new registration information to the table
        """
        try:
            self.table.put_item(
                Item={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "reg_date": reg_date,
                    "address": address,
                    "shirt_size": shirt_size,
                    "pick_up_event_day": pick_up_event_day,
                }
            )
        except ClientError as err:
            logger.error(
                "Couldn't add the registration for %s %s to table %s. Here's why: %s: %s",
                first_name,
                last_name,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        
def main(table_name="Registration"):
    dyn_resource = boto3.resource("dynamodb")

    registration = Registration(dyn_resource)
    table_exists = registration.exists(table_name)

    if not table_exists:
        print(f"\nCreating table {table_name}...")
        registration.create_table(table_name)
        print(f"\nCreated table {registration.table.name}.")
    print(f"Adding item to the {table_name} table")

    registration.add_registration("John", "Doe", "jdoe@example.com", "12/09/2024", "123 Example St, Gotham, NJ, 07748", "M", False)
            
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error occurred!", e)