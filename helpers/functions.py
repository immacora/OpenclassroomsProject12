from locations.models import Location


def add_locations_to_model(model_instance, location_data):
    for location_item in location_data:
        location, created = Location.objects.get_or_create(**location_item)
        model_instance.locations.add(location)
