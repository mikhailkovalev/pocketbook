# Generated by Django 2.1.5 on 2021-05-02 13:55
from datetime import date

from django.db import migrations, models
import django.db.models.deletion


def forwards_injections(apps, schema_editor):
    InsulinInjection = apps.get_model('sugar', 'InsulinInjection')
    InsulinSyringe = apps.get_model('sugar', 'InsulinSyringe')

    pairs = set(InsulinInjection.objects.values_list(
        'record__who_id',
        'insulin_mark',
    ).distinct())

    for user_id, insulin_mark_id in pairs:
        fake_syringe = InsulinSyringe.objects.create(
            whose_id=user_id,
            volume=0,
            opening=date.min,
            expiry_plan=None,
            expiry_actual=date.today(),
            insulin_mark_id=insulin_mark_id,
        )
        InsulinInjection.objects.filter(
            record__who_id=user_id,
            insulin_mark_id=insulin_mark_id,
        ).update(
            insulin_syringe=fake_syringe,
        )


def backwards_injections(apps, schema_editor):
    InsulinInjection = apps.get_model('sugar', 'InsulinInjection')
    InsulinInjection.objects.update(
        insulin_mark=models.F('insulin_syringe__insulin_mark'),
    )


def forwards_meterings(apps, schema_editor):
    SugarMetering = apps.get_model('sugar', 'SugarMetering')
    TestStripPack = apps.get_model('sugar', 'TestStripPack')
    users_ids = set(SugarMetering.objects.values_list(
        'record__who_id',
        flat=True,
    ).distinct())

    for user_id in users_ids:
        fake_pack = TestStripPack.objects.create(
            whose_id=user_id,
            volume=0,
            opening=date.min,
            expiry_plan=None,
            expiry_actual=date.today(),
        )
        SugarMetering.objects.filter(
            record__who_id=user_id,
        ).update(
            pack=fake_pack,
        )


def backwards_meterings(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sugar', '0004_insulinordering_insulinsyringe_teststrippack'),
    ]

    operations = [
        migrations.AddField(
            model_name='insulininjection',
            name='insulin_syringe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='injections', to='sugar.InsulinSyringe', verbose_name='Шприц'),
        ),
        migrations.AddField(
            model_name='sugarmetering',
            name='pack',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='meterings', to='sugar.TestStripPack', verbose_name='Пачка'),
        ),
        migrations.RunPython(
            code=forwards_injections,
            reverse_code=backwards_injections,
        ),
        migrations.RunPython(
            code=forwards_meterings,
            reverse_code=backwards_meterings,
        ),
        migrations.AlterField(
            model_name='insulininjection',
            name='insulin_syringe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='injections', to='sugar.InsulinSyringe', verbose_name='Шприц'),
        ),
        migrations.AlterField(
            model_name='sugarmetering',
            name='pack',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='meterings', to='sugar.TestStripPack', verbose_name='Пачка'),
        ),
        migrations.RemoveField(
            model_name='insulininjection',
            name='insulin_mark',
        ),
    ]