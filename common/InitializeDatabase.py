from acquisition_presentation_server.models import MonitoredProperties

def initialize_database():
    choices = MonitoredProperties.get_possible_choices()
    for choice in choices:
        MonitoredProperties.objects.get_or_create(property_name=choice)