from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
tipoOficina = [('Administrativo','Administrativo'),('Formacion','Formacion')]
tipoUsuario = [('Administrativo','Administrativo'),('Instructor','Instructor')]
estadocaso = [('Solicitada','Solicitada'),('En Proceso','En Proceso'),('Finalizada','Finalizada')]
tipoSolucion = [('Parcial', 'Parcial'),('Definitiva', 'Definitiva')]

# tipoProcedimiento = [('Software','Software'),('Hadware','Hadware'),('','')]

class oficinaAmbiente (models.Model):
    ofi_tipo = models.CharField(max_length=30, choices=tipoOficina,db_comment="tipo de oficina" )
    ofi_nombre = models.CharField(max_length=60, unique=True,db_comment="Nombre oficina o ambiente")
    fecha_hora_creacion = models.DateTimeField(auto_now_add=True,                                   db_comment="Fecha y hora de creacion")
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True,
                                                    db_comment="Fecha y hora de actualizacion")

    def __str__(self) -> str:
        return self.ofi_nombre



class User (AbstractUser):
    user_tipo = models.CharField(max_length=15,choices=tipoUsuario, db_comment="Tipo de usuario")
    user_foto = models.ImageField(upload_to=f"fotos/", null=True, blank=True, db_comment="Foto del usuario")
    fecha_hora_creacion = models.DateTimeField(auto_now_add=True,
                                             db_comment="Fecha y hora de creacion")
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True,
                                                    db_comment="Fecha y hora de actualizacion")
    def __str__(self) -> str: 
        return self.username

class Solicitud (models.Model):
    sol_usuario = models.ForeignKey(User,on_delete=models.PROTECT, db_comment="hace referencia al empleado que hace la solicitud")
    sol_descripcion = models.TextField(max_length=1000, db_comment="Texto que describe la solicitud del empleado")
    sol_oficina_ambiente = models.ForeignKey(oficinaAmbiente, on_delete=models.PROTECT,db_comment="Hace referencia a la oficia o ambiente donde se encuentra el equipo de la solicitud")
    fecha_hora_creacion = models.DateField(auto_now_add=True,
                                             db_comment="Fecha y hora de creacion")
    fecha_hora_actualizacion = models.DateField(auto_now=True,
                                                    db_comment="Fecha y hora de actualizacion")

    def __str__(self):
        return self.sol_descripcion

class Caso (models.Model):
    cas_solicitud = models.ForeignKey(Solicitud, on_delete=models.PROTECT, db_comment="Hace referencia a la solicitud que hace el caso")
    cas_codigo = models.CharField(max_length=20, unique=True, db_comment="Codigo unico del caso")
    cas_usuario = models.ForeignKey(User, on_delete=models.PROTECT, db_comment ="Empleado de soporte tecnico asignado al caso")
    cas_estado = models.CharField(max_length=15, choices=estadocaso, db_comment="Eleccion del estado del caso",default='Solicitada')
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True,
                                                    db_comment="Fecha y hora de actualizacion")
    def __str__(self):
     return self.cas_estado
    
class TipoProcedimiento (models.Model):
    tip_pro_nombre = models.CharField(max_length=20, unique=True, db_comment="Procedimientos a realizar")
    tip_pro_descripcion = models.TextField(max_length=1000,
                                           db_comment="Texto con la descripcion del procedimiento")
    fecha_hora_creacion = models.DateTimeField(auto_now_add=True,
                                             db_comment="Fecha y hora de creacion")
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True,
                                                    db_comment="Fecha y hora de actualizacion")
    def __str__(self):
        return self.tip_pro_nombre


class SolucionCaso(models.Model):
    sol_caso = models.ForeignKey(Caso, on_delete=models.PROTECT,
                                db_comment="Hace referencia al caso que genera la solución")
    sol_procedimiento = models.TextField(max_length=2000,
                                        db_comment="Texto del procedimiento realizado en la solución del caso")
    solTipoSolucion = models.CharField(max_length=20, choices=tipoSolucion,
                                       db_comment="Tipo de la solucuín, si es parcial o definitiva")
    fecha_hora_creacion = models.DateTimeField(auto_now_add=True,
                                             db_comment="Fecha y hora de creacion")
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True,
                                                    db_comment="Fecha y hora de actualizacion")
    def __str__(self):
        return self.sol_procedimiento


class solucionCasotipoProcedimiento (models.Model):
    sp_solucion_caso =models.ForeignKey(SolucionCaso, on_delete=models.PROTECT, db_comment="Llave foranea de Solucion del caso")
    sp_tipo_procedimiento =models.ForeignKey(TipoProcedimiento, on_delete=models.PROTECT, db_comment="Llave foranea de Solucion de Tipo de procedimiento")
    def __str__(self):
        return f"{self.sp_solucion_caso},{self.sp_tipo_procedimiento}"