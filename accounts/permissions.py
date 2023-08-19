from django.contrib.auth.models import Permission


def add_default_permissions_to_groups(management_group, sales_group, support_group):
    """
    Add each required permission by default to groups.
    In accordance with company document retention periods,/
    permissions to delete customer information are not available by default.
    Only the management_group can access the CRUD of the user and employee models,/
    add and change contracts, and change_event.
    All employees can see location, client, contract and event models.
    Sales_group and support_group can add and change location model.
    Only the sales_group can add client.
    """

    add_user = Permission.objects.get(codename="add_customuser")
    change_user = Permission.objects.get(codename="change_customuser")
    view_user = Permission.objects.get(codename="view_customuser")

    add_employee = Permission.objects.get(codename="add_employee")
    change_employee = Permission.objects.get(codename="change_employee")
    delete_employee = Permission.objects.get(codename="delete_employee")
    view_employee = Permission.objects.get(codename="view_employee")

    add_location = Permission.objects.get(codename="add_location")
    change_location = Permission.objects.get(codename="change_location")
    view_location = Permission.objects.get(codename="view_location")

    add_client = Permission.objects.get(codename="add_client")
    view_client = Permission.objects.get(codename="view_client")

    add_contract = Permission.objects.get(codename="add_contract")
    change_contract = Permission.objects.get(codename="change_contract")
    view_contract = Permission.objects.get(codename="view_contract")

    change_event = Permission.objects.get(codename="change_event")
    view_event = Permission.objects.get(codename="view_event")

    management_group.permissions.set(
        [
            add_user,
            change_user,
            view_user,
            add_employee,
            change_employee,
            delete_employee,
            view_employee,
            view_location,
            view_client,
            add_contract,
            change_contract,
            view_contract,
            change_event,
            view_event,
        ]
    )
    sales_group.permissions.set(
        [
            add_location,
            change_location,
            view_location,
            add_client,
            view_client,
            view_contract,
            view_event,
        ]
    )
    support_group.permissions.set([add_location, change_location, view_location])
