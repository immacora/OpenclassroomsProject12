import uuid

from accounts.models import Employee
from apis.serializers import ClientDetailSerializer


def check_uuid_value(uuid_value):
    """Return error message or None."""
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
