from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib import auth
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from MesaAyuda.models import *
from random import randint
from django.db import Error,transaction
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading
from smtplib import SMTPException
from django.http import JsonResponse

# Create your views here.

def inicio (request):
    return render(request, 'login.html')

@csrf_exempt
def login(request):
    username = request.POST['correo']
    password = request.POST['contraseña']
    user = authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        if user.groups.filter(name='administrador').exists():
            return redirect('/inicioAdministrador')
        elif user.groups.filter(name='tecnico').exists():
            return redirect('/inicioTecnico')
        else: 
            return redirect('/inicioEmpleado')
    else:
        mensaje =  'Usuario o Clave incorrectas'
        return render(request, 'login.html', {'mensaje': mensaje})
    

def Administrador (request):
    return render (request, "administrador/inicio.html")

def inicioAdministrador (request):
    if request.user.is_authenticated:
        datosSesion = {"user":request.user,
                       "rol":request.user.groups.get().name}
        return render (request, "administrador/inicio.html", datosSesion)
    else:
        mensaje ="Debe iniciar Sesion"
        return render (request, "login.html", {"mensaje":mensaje})
    
def inicioTecnico(request):
    if request.user.is_authenticated:
        datosSesion = {"user":request.user,
                       "rol":request.user.groups.get().name}
        return render (request, "tecnico/inicio.html", datosSesion)
    else:
        mensaje ="Debe iniciar Sesion"
        return render (request, "login.html", {"mensaje":mensaje})
    
def inicioEmpleado(request):
    if request.user.is_authenticated:
        datosSesion = {"user":request.user,
                       "rol":request.user.groups.get().name}
        return render (request, "empleado/inicio.html", datosSesion)
    else:
        mensaje ="Debe iniciar Sesion"
        return render (request, "login.html", {"mensaje":mensaje})
    
@csrf_exempt    
def registroSolicitud (request):
    try:
        with transaction.atomic():
            user = request.user
            descripcion = request.POST["descripcion"]
            idOficinaAmbiente = request.POST["idOficinaAmbiente"]
            oficinaAmbient = oficinaAmbiente.objects.get(pk=idOficinaAmbiente)
            solicitud = Solicitud(sol_usuario=user,sol_descripcion=descripcion,sol_oficina_ambiente=oficinaAmbient)
            solicitud.save()
            
            fecha = datetime.now()
            year = fecha.year
            
            consecutivoCaso = Solicitud.objects.filter(fecha_hora_creacion__year = year).count()
            codigoCaso = f"REQ-{year}-{consecutivoCaso}"
            
            userCaso = User.objects.filter(
                groups__name__in=['Administrador']).first()

            caso = Caso(cas_solicitud=solicitud,
                        cas_codigo = codigoCaso,
                        cas_usuario = userCaso)
            caso.save()
            
            asunto = 'Registro Solicitud - Mesa de Servicio'
            mensajeCorreo = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
                informarle que su solicitud fue registrada en nuestro sistema con el número de caso \
                <b>{codigoCaso}</b>. <br><br> Su caso será gestionado en el menor tiempo posible, \
                según los acuerdos de solución establecidos para la Mesa de Servicios del CTPI-CAUCA.\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la siguiente url:\
                http://mesadeservicioctpicauca.sena.edu.co.'
            # crear el hilo para el envío del correo
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensajeCorreo, [user.email]))
            # ejecutar el hilo
            thread.start()
            mensaje = "Se ha registrado su solicitud de manera exitosa"
    # Enviar el correo al empleado
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
        return render(request, "empleado/solicitud.html", {"mensaje":mensaje})


    oficinaAmbientes = oficinaAmbiente.objects.all()
    retorno = {"mensaje": mensaje, "oficinasAmbientes": oficinaAmbientes}
    return render(request, "empleado/solicitud.html", retorno)    
        
def vistaSolicitud(request):
    if request.user.is_authenticated:
        oficinaAmbientes = oficinaAmbiente.objects.all()
        datosSesion = {"user":request.user,
                       "rol":request.user.groups.get().name,
                       "oficinaAmbientes":oficinaAmbientes}
                       
        return render (request, "empleado/solicitud.html",datosSesion)
    else:
        mensaje="Debes iniciar sesion"
        return render (request,"login.html",{"mensaje":mensaje})

    
def enviarCorreo(asunto=None, mensaje=None, destinatario=None,archivo=None):
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'mensaje':mensaje,
    })
    try:
        correo = EmailMultiAlternatives(
            asunto, mensaje, remitente, destinatario
        )
        correo.attach_alternative(contenido,'text/html')
        if archivo != None :
            correo.attach_file(archivo)
        correo.send(fail_silently=True)
    except SMTPException as error:
        print (error)

    
def listarCasos (request):
    try:
        mensaje=""
        listarCasos = Caso.objects.all()
        tecnicos = User.objects.filter(groups__name__in=['Tecnico'])
    except Error as error :
        mensaje=str(error)
    
    retorno = {"listarCasos":listarCasos, "tecnicos":tecnicos, "mensaje":mensaje}
    return render (request, "administrador/listarCasos.html", retorno)


def listarEmpleadosTecnicos(request):
    try:
        mensaje =""
        tecnicos = User.objects.filter(groups_name_in=['Tecnico'])
    except Error as error:
     mensaje=str(error)
    retorno = {"tecnicos":tecnicos, "mensaje":mensaje}
    return JsonResponse(retorno)

def asignarTecnicoCaso (request):
    if request.user.is_authenticated:
        try:
            idTecnico = int(request.POST['cbTecnico'])
            userTecnico = User.objects.get(pk=idTecnico)
            idCaso = int(request.POST['idCaso'])
            caso = Caso.objects.get(pk=idCaso)
            caso.cas_usuario=userTecnico
            caso.cas_estado="En Proceso"
            caso.save()
            ## Enviar Correo al tecnico
            asunto = 'Asignacion Caso - Mesa de Servicio'
            mensajeCorreo = f'Cordial saludo, <b>{userTecnico.first_name} {userTecnico.last_name}</b>, nos permitimos \
                informarle que se le ha asignado un caso para dar solucion. Codigo de Caso: \
                <b>{caso.cas_codigo}</b>.Se solicita se atienda de manera opurtuna \
                según los acuerdos de solución establecidos para la Mesa de Servicios del CTPI-CAUCA.\
                <br><br>Lo invitamos a ingresar al sistema para gestionar sus casos asignados:\
                http://mesadeservicioctpicauca.sena.edu.co.'
            # crear el hilo para el envío del correo
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensajeCorreo, [userTecnico.email]))
            # ejecutar el hilo
            thread.start()
            mensaje = "Caso asignado"
            return redirect('/listarCasosParaAsignar/')
            
        except Error as error:
            mensaje=str(error)
    else:
        mensaje="Debes iniciar sesion"
        return render (request,"login.html",{"mensaje":mensaje})    

def salir (request):
    auth.logout(request)
    mensaje = "Se ha cerrado sesion"
    return redirect('/')