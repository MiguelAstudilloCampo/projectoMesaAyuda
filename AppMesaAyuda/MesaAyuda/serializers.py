from rest_framework import serializers
from MesaAyuda.models import *

class oficinaAmbienteSerializer (serializers.ModelSerializer):
    class Meta :
        model = oficinaAmbiente
        fields = '__all__'