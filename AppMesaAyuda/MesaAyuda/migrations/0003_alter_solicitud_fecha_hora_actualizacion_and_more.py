# Generated by Django 4.2.13 on 2024-06-24 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MesaAyuda', '0002_alter_caso_cas_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitud',
            name='fecha_hora_actualizacion',
            field=models.DateField(auto_now=True, db_comment='Fecha y hora de actualizacion'),
        ),
        migrations.AlterField(
            model_name='solicitud',
            name='fecha_hora_creacion',
            field=models.DateField(auto_now_add=True, db_comment='Fecha y hora de creacion'),
        ),
    ]
