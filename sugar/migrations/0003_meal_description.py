# Generated by Django 2.0.7 on 2019-12-21 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sugar', '0002_auto_20190909_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='description',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Описание'),
        ),
    ]
