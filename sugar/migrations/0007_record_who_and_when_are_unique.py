# Generated by Django 2.1.5 on 2021-09-15 22:11

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sugar', '0006_auto_20210613_2238'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='record',
            unique_together={('who', 'when')},
        ),
    ]