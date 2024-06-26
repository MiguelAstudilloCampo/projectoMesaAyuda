# Generated by Django 4.2.13 on 2024-05-27 13:38

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Caso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cas_codigo', models.CharField(db_comment='Codigo unico del caso', max_length=20, unique=True)),
                ('cas_estado', models.CharField(choices=[('Solicitada', 'Solicitada'), ('En Proceso', 'En Proceso'), ('Finalizada', 'Finalizada')], db_comment='Eleccion del estado del caso', max_length=15)),
                ('fecha_hora_actualizacion', models.DateTimeField(auto_now=True, db_comment='Fecha y hora de actualizacion')),
            ],
        ),
        migrations.CreateModel(
            name='oficinaAmbiente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ofi_tipo', models.CharField(choices=[('Administrativo', 'Administrativo'), ('Formacion', 'Formacion')], db_comment='tipo de oficina', max_length=30)),
                ('ofi_nombre', models.CharField(db_comment='Nombre oficina o ambiente', max_length=60, unique=True)),
                ('fecha_hora_creacion', models.DateTimeField(auto_now_add=True, db_comment='Fecha y hora de creacion')),
                ('fecha_hora_actualizacion', models.DateTimeField(auto_now=True, db_comment='Fecha y hora de actualizacion')),
            ],
        ),
        migrations.CreateModel(
            name='SolucionCaso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sol_procedimiento', models.TextField(db_comment='Texto del procedimiento realizado en la solución del caso', max_length=2000)),
                ('solTipoSolucion', models.CharField(choices=[('Parcial', 'Parcial'), ('Definitiva', 'Definitiva')], db_comment='Tipo de la solucuín, si es parcial o definitiva', max_length=20)),
                ('fecha_hora_creacion', models.DateTimeField(auto_now_add=True, db_comment='Fecha y hora de creacion')),
                ('fecha_hora_actualizacion', models.DateTimeField(auto_now=True, db_comment='Fecha y hora de actualizacion')),
                ('sol_caso', models.ForeignKey(db_comment='Hace referencia al caso que genera la solución', on_delete=django.db.models.deletion.PROTECT, to='MesaAyuda.caso')),
            ],
        ),
        migrations.CreateModel(
            name='TipoProcedimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tip_pro_nombre', models.CharField(db_comment='Procedimientos a realizar', max_length=20, unique=True)),
                ('tip_pro_descripcion', models.TextField(db_comment='Texto con la descripcion del procedimiento', max_length=1000)),
                ('fecha_hora_creacion', models.DateTimeField(auto_now_add=True, db_comment='Fecha y hora de creacion')),
                ('fecha_hora_actualizacion', models.DateTimeField(auto_now=True, db_comment='Fecha y hora de actualizacion')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_tipo', models.CharField(choices=[('Administrativo', 'Administrativo'), ('Instructor', 'Instructor')], db_comment='Tipo de usuario', max_length=15)),
                ('user_foto', models.ImageField(blank=True, db_comment='Foto del usuario', null=True, upload_to='fotos/')),
                ('fecha_hora_creacion', models.DateTimeField(auto_now_add=True, db_comment='Fecha y hora de creacion')),
                ('fecha_hora_actualizacion', models.DateTimeField(auto_now=True, db_comment='Fecha y hora de actualizacion')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='solucionCasotipoProcedimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sp_solucion_caso', models.ForeignKey(db_comment='Llave foranea de Solucion del caso', on_delete=django.db.models.deletion.PROTECT, to='MesaAyuda.solucioncaso')),
                ('sp_tipo_procedimiento', models.ForeignKey(db_comment='Llave foranea de Solucion de Tipo de procedimiento', on_delete=django.db.models.deletion.PROTECT, to='MesaAyuda.tipoprocedimiento')),
            ],
        ),
        migrations.CreateModel(
            name='Solicitud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sol_descripcion', models.TextField(db_comment='Texto que describe la solicitud del empleado', max_length=1000)),
                ('fecha_hora_creacion', models.DateTimeField(auto_now_add=True, db_comment='Fecha y hora de creacion')),
                ('fecha_hora_actualizacion', models.DateTimeField(auto_now=True, db_comment='Fecha y hora de actualizacion')),
                ('sol_oficina_ambiente', models.ForeignKey(db_comment='Hace referencia a la oficia o ambiente donde se encuentra el equipo de la solicitud', on_delete=django.db.models.deletion.PROTECT, to='MesaAyuda.oficinaambiente')),
                ('sol_usuario', models.ForeignKey(db_comment='hace referencia al empleado que hace la solicitud', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='caso',
            name='cas_solicitud',
            field=models.ForeignKey(db_comment='Hace referencia a la solicitud que hace el caso', on_delete=django.db.models.deletion.PROTECT, to='MesaAyuda.solicitud'),
        ),
        migrations.AddField(
            model_name='caso',
            name='cas_usuario',
            field=models.ForeignKey(db_comment='Empleado de soporte tecnico asignado al caso', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
