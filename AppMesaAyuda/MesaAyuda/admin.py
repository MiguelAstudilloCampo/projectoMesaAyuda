from django.contrib import admin
from MesaAyuda.models import oficinaAmbiente, User, TipoProcedimiento

# Register your models here.

admin.site.register(oficinaAmbiente)
admin.site.register(TipoProcedimiento)
admin.site.register(User)
