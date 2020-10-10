# Generated by Django 2.1 on 2020-10-10 14:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Наименование')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='money.Account', verbose_name='Обобщение')),
            ],
            options={
                'verbose_name': 'Счёт',
                'verbose_name_plural': 'Счета',
            },
        ),
        migrations.CreateModel(
            name='AccountHierarchy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(choices=[('active', 'Активный'), ('passive', 'Пассивный'), ('income', 'Приход'), ('expense', 'Расход')], max_length=8, verbose_name='Тип счёта')),
                ('root', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='money.Account', verbose_name='Корневой элемент иерархии')),
                ('whose', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Владелец иерархии')),
            ],
            options={
                'verbose_name': 'Иерархия счетов',
                'verbose_name_plural': 'Иерархии счетов',
            },
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Остаток')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='money.Account', verbose_name='Счёт')),
            ],
            options={
                'verbose_name': 'Остаток средств',
                'verbose_name_plural': 'Остатки средств',
            },
        ),
        migrations.CreateModel(
            name='BalanceFixation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(verbose_name='Момент фиксации')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('prev_fixation', mptt.fields.TreeOneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='next_fixation', to='money.BalanceFixation', verbose_name='Предыдущая фиксация')),
            ],
            options={
                'verbose_name': 'Фиксация остатков',
                'verbose_name_plural': 'Фиксации остатков',
                'ordering': ('-when',),
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Наименование')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='money.Provider', verbose_name='Обобщение')),
            ],
            options={
                'verbose_name': 'Источник/получатель платежа',
                'verbose_name_plural': 'Источники/получатели платежей',
            },
        ),
        migrations.CreateModel(
            name='ProviderHierarchy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('root', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='money.Provider', verbose_name='Корневой элемент иерархии')),
                ('whose', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Владелец иерархии')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateField(verbose_name='Дата операции')),
                ('value', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Сумма операции')),
                ('credit_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='credit_transfers', to='money.Account', verbose_name='Счёт списания')),
                ('debit_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='debit_transfers', to='money.Account', verbose_name='Счёт зачисления')),
                ('fixation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers', to='money.BalanceFixation', verbose_name='Фиксация, в которой учтена эта операция')),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='money.Provider', verbose_name='Источник/получатель платежа')),
            ],
            options={
                'verbose_name': 'Операция',
                'verbose_name_plural': 'Операции',
                'ordering': ('-when',),
            },
        ),
        migrations.CreateModel(
            name='TransferDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Наименование')),
                ('count', models.DecimalField(decimal_places=3, max_digits=15, verbose_name='Количество товара/услуг')),
                ('cost', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Цена за единицу')),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='money.Transfer', verbose_name='Операция')),
            ],
            options={
                'verbose_name': 'Деталь операции',
                'verbose_name_plural': 'Детали операций',
            },
        ),
        migrations.AddField(
            model_name='balance',
            name='fixation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='money.BalanceFixation', verbose_name='Фиксация'),
        ),
        migrations.AlterUniqueTogether(
            name='balance',
            unique_together={('account', 'fixation')},
        ),
        migrations.AlterUniqueTogether(
            name='accounthierarchy',
            unique_together={('whose', 'activity')},
        ),
    ]