import uuid

from locations.models import Location
from accounts.models import Employee
from apis.serializers import ClientDetailSerializer


def add_locations(model_instance, location_data):
    for location_item in location_data:
        location, created = Location.objects.get_or_create(**location_item)
        model_instance.locations.add(location)


def remove_locations(model_instance, location_id):
    """Remove location from model if it belongs to it
    and delete location from the application if it is not used by other clients or events.
    """
    for location_item in model_instance.locations.all():
        if str(location_item.location_id) == location_id:
            model_instance.locations.remove(location_item.location_id)
            locations = Location.objects.all()
            for location in locations:
                if location_id == str(location.location_id):
                    if (
                        location.client_locations.count() == 0
                        and location.event_locations.count() == 0
                    ):
                        location.delete()


def check_uuid_value(uuid_value):
    try:
        uuid.UUID(str(uuid_value))
    except ValueError:
        return "Veuillez saisir un UUID valide."


def update_sales_contact(client_instance, updated_sales_contact_id):
    """Update client sales_contact if field is correct uuid and employee exists or return error message."""

    sales_contact_uuid = check_uuid_value(updated_sales_contact_id)
    if not isinstance(sales_contact_uuid, str):
        try:
            employee = Employee.objects.get(employee_id=updated_sales_contact_id)
            if not employee.department == "SALES":
                return "Le sales_contact doit être un employé du département ventes."
            client_instance.sales_contact = employee
            client_instance.save()
            client_data = ClientDetailSerializer(client_instance).data
            return client_data
        except Employee.DoesNotExist:
            return "Il n'existe pas d'employé correspondant à cet identifiant."
    else:
        return sales_contact_uuid
