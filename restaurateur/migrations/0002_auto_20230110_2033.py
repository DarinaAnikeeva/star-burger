from restaurateur.models import Coordinates
from django.db import migrations

def coordinates(apps, schema_editor):
    Coordinates_1 = apps.get_model('restaurateur', 'Coordinates')
    for coordinates in Coordinates_1.objects.all().iterator():
        Coordinates.objects.create(
            address=coordinates.address,
            lon=coordinates.lon,
            lat=coordinates.lat
        )


class Migration(migrations.Migration):

    dependencies = [
        ('restaurateur', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(coordinates)
    ]
