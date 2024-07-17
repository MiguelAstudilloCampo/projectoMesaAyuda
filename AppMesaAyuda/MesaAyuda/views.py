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

import random
import string
from django.contrib.auth.models import Group

from django.db.models import Sum, Avg, Count
import matplotlib.pyplot as plt
import calendar
from django.db.models.functions import ExtractMonth

from rest_framework import generics
from MesaAyuda.serializers import oficinaAmbienteSerializer

import os

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

def listarCasosTecnico (request):
    if request.user.is_authenticated:
        try:
            ListaCasos = Caso.objects.filter(cas_estado="En Proceso", cas_usuario=request.user)
            listaTipoProcedimiento = TipoProcedimiento.objects.all().values()
            mensaje = "Listado de casos asignados"
        except Error as error:
            mensaje=str(error)
        retorno = {"mensaje":mensaje, "ListaCasos":ListaCasos, "listaTipoSolucion":tipoSolucion,"listaTipoProcedimiento":listaTipoProcedimiento}
        return render(request, "tecnico/listaCasosAsignados.html", retorno)
    
    else:
        mensaje="Debes iniciar sesion"
        return render (request,"login.html",{"mensaje":mensaje})

def solucionarCaso (request):
    if request.user.is_authenticated:
        try:
            if transaction.atomic():
                procedimiento = request.POST["procedimiento"]
                tipoProc = request.POST ["cbTipoProcedimiento"]
                tipoProcedimiento = TipoProcedimiento.objects.get(pk=tipoProc)
                tipoSolucion = request.POST['cbTipoSolucion']
                idCaso = int(request.POST['idCaso'])
                caso = Caso.objects.get(pk=idCaso)
                solucionCaso = SolucionCaso(sol_caso=caso,sol_procedimiento=procedimiento, solTipoSolucion = tipoSolucion)
                solucionCaso.save()

                if (tipoSolucion=="Definitiva"):
                    caso.cas_estado="Finalizada"
                    caso.save()


                SolucionCasotipoProcedimiento = solucionCasotipoProcedimiento(
                    sp_solucion_caso=solucionCaso,
                    sp_tipo_procedimiento=tipoProcedimiento
                ) 
                
                SolucionCasotipoProcedimiento.save()
                
                ## Enviar Correo
                
                solicitud=caso.cas_solicitud
                userEmpleado = solicitud.sol_usuario
                
                asunto = 'Solucion Caso - Mesa de Servicio'
                mensajeCorreo = f'Cordial saludo, <b>{userEmpleado.first_name} {userEmpleado.last_name}</b>, nos permitimos \
                informarle que se le ha dado solucion de tipo {tipoSolucion} al caso identificado con codigo: \. Codigo de Caso: \
                    <b>{caso.cas_codigo}</b>.Lo invitamos a revisar el equipo y verificar la solucion. \
                    según los acuerdos de solución establecidos para la Mesa de Servicios del CTPI-CAUCA.\
                    <br><br>Para consultar en detalle la solucion  ingresar al sistema para verificar las solicitudes\
                    http://mesadeservicioctpicauca.sena.edu.co.'
                # crear el hilo para el envío del correo
                thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensajeCorreo, [userEmpleado.email]))
                # ejecutar el hilo
                thread.start()
                mensaje="Solucion Caso"
                
        except Error as error:
            transaction.rollback()
            mensaje=str(error)
        
        retorno = {"mensaje":mensaje}
        return redirect ("/listarCasosAsignados/")
            
            
    else:
        mensaje="Debes iniciar sesion"
        return render (request,"login.html",{"mensaje":mensaje})

def generarPassword ():
    longitud = 10
    
    caracteres = string.ascii_lowercase + \
        string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    
    for i in range(longitud):
        password += '' .join(random.choice(caracteres))
    return password

def vistaRegistrarUsuario(request):
    if request.user.is_authenticated:
        roles = Group.objects.all()
        retorno = {"roles": roles, "user": request.user, 'tipoUsuario': tipoUsuario,
                   "rol": request.user.groups.get().name}
        return render(request, "administrador/registrarUsuario.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "registrarUsuario.html", {"mensaje": mensaje})

def registrarUsuario(request):
    if request.user.is_authenticated:
        try:
            nombres = request.POST["nombres"]
            apellidos = request.POST["apellidos"]
            correo = request.POST["correo"]
            tipo = request.POST["cbTipo"]
            foto = request.FILES.get("foto")
            idRol = int(request.POST["cbRol"])
            with transaction.atomic():
                user = User(username=correo, first_name=nombres,
                            last_name=apellidos, email=correo, user_tipo=tipo, user_foto=foto)
                user.save()
                rol = Group.objects.get(pk=idRol)
                user.groups.add(rol)
                if (rol.name == "Administrador"):
                    user.is_staff = True
                user.save()
                passwordGenerado = generarPassword()
                print(f"password {passwordGenerado}")
                user.set_password(passwordGenerado)
                user.save()
                mensaje = "Usuario Agregado Correctamente"
                retorno = {"mensaje": mensaje}
                asunto = 'Registro Sistema Mesa de Servicio CTPI-CAUCA'
                mensaje = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
                    informarle que usted ha sido registrado en el Sistema de Mesa de Servicio \
                    del Centro de Teleinformática y Producción Industrial CTPI de la ciudad de Popayán, \
                    con el Rol: <b>{rol.name}</b>. \
                    <br>Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                    <br><b>Username: </b> {user.username}\
                    <br><b>Password: </b> {passwordGenerado}\
                    <br><br>Lo invitamos a utilizar el aplicativo, donde podrá usted \
                    realizar solicitudes a la mesa de servicio del Centro. Url del aplicativo: \
                    http://mesadeservicioctpi.sena.edu.co.'
                thread = threading.Thread(
                    target=enviarCorreo, args=(asunto, mensaje, [user.email]))
                thread.start()
                return redirect("/vistaGestionarUsuarios/", retorno)
        except Error as error:
            transaction.rollback()
            mensaje = f"{error}"
        retorno = {"mensaje": mensaje}
        return render(request, "administrador/registrarUsuario.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "login.html", {"mensaje": mensaje})

def recuperarClave(request):
    try:
        correo = request.POST['correo']
        user = User.objects.filter(email=correo).first()
        if (user):
            passwordGenerado = generarPassword()
            user.set_password(passwordGenerado)
            user.save()
            mensaje = "Contraseña Actualiza Correctamente y enviada al Correo Electrónico"
            retorno = {"mensaje": mensaje}
            asunto = 'Recuperación de Contraseña Sistema Mesa de Servicio CTPI-CAUCA'
            mensaje = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
                    informarle que se ha generado nueva contraseña para ingreso al sistema. \
                    <br><b>Username: </b> {user.username}\
                    <br><b>Password: </b> {passwordGenerado}\
                    <br><br>Para comprobar ingresar al sistema haciendo uso de la nueva contraseña.'
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensaje, [user.email]))
            thread.start()
        else:
            mensaje = "No existe usuario con correo ingresado. Revisar"
            retorno = {"mensaje": mensaje}
    except Error as error:
        mensaje = str(error)

    return render(request, 'login.html', retorno)

def vistaGestionarUsuarios(request):
    if request.user.is_authenticated:
        usuarios = User.objects.all()
        retorno = {"usuarios": usuarios, "user": request.user,
                   "rol": request.user.groups.get().name}
        return render(request, "administrador/gestionarUsuarios.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "login.html", {"mensaje": mensaje})

# def estadistica (request):
#     if request.user.is_authenticated:
#         try:
#             return redirect("/graficas/")
#         except Error as error:
#             transaction.rollback()
#             mensaje = f"{error}"
#         return render(request, "administrador/inicio.html")
#     else:
#         mensaje = "Debe iniciar sesión"
#         return render(request, "login.html", {"mensaje": mensaje})
    
def estadisticas(request):
    import matplotlib
    if request.user.is_authenticated:
        matplotlib.use('agg')
        listaAmbientes = oficinaAmbiente.objects.all()
        listaSolicitudes = Solicitud.objects.all()

        # grafico cantidad solicitudes por ambiente
        solicitudesPorAmbiente = Solicitud.objects.values('sol_oficina_ambiente')\
            .annotate(cantidad=Count('id'))
        xAmbiente = []
        yCantidadAmbiente = []
        for ambiente in listaAmbientes:
            for solicitud in listaSolicitudes:
                if ambiente.id == solicitud.sol_oficina_ambiente.id:
                    xAmbiente.append(ambiente)
                    yCantidadAmbiente.append(0)
                    break
        i = 0
        colores = []
        for ambiente in xAmbiente:
            for solicitud in listaSolicitudes:
                if ambiente.id == solicitud.sol_oficina_ambiente.id:
                    yCantidadAmbiente[i] += 1
                    color = "#" + \
                        ''.join([random.choice('0123456789ABCDEF')
                                for j in range(6)])
                    colores.append(color)
            i += 1
        textprops = {"fontsize": 6}
        plt.title("Cantidad de Solicitudes Realizadas \n por Ambiente")
        plt.pie(yCantidadAmbiente, labels=xAmbiente,
                autopct="%0.1f %%", textprops=textprops, colors=colores)
        rutaImagen = os.path.join(settings.MEDIA_ROOT + "\\" + "grafica1.png")
        plt.savefig(rutaImagen)
        plt.close()

        # grafica cantidad solicitudes por mes
        solicitudesPorMes = Solicitud.objects.values(mes=ExtractMonth('fecha_hora_creacion'))\
            .annotate(cantidad=Count('id'))
        yCantidadMes = []
        meses = []
        textoMes = ['Enero', 'Febrero', 'Marzo',
                    'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto']
        colores = []
        for solicitud in solicitudesPorMes:
            meses.append(textoMes[solicitud['mes']-1])
            yCantidadMes.append(solicitud['cantidad'])
            color = "#" + \
                ''.join([random.choice('0123456789ABCDEF')
                         for j in range(6)])
            colores.append(color)

        textprops = {"fontsize": 10}
        plt.title("Cantidad de Solicitudes Realizadas \n por Mes")
        plt.bar(meses, yCantidadMes, color=colores)
        rutaImagen = os.path.join(settings.MEDIA_ROOT + "\\" + "grafica2.png")
        plt.savefig(rutaImagen)
        plt.close()

        '''
        casosPorTipo = SolucionCasoTipoProcedimientos.objects.values(tipo='solTipoProcedimiento__tipNombre')\
            .annotate(cantidad=Count('solSolucionCaso__id'))

        yCantidadCasosTipo = []
        tiposProcedimientos = []

        tipos = TipoProcedimiento.objects.all()
        for tipo in tipos:
            tiposProcedimientos.append(tipo)
            yCantidadCasosTipo.append(0)

        i = 0
        for caso in casosPorTipo:
            for tipo in tipos:
                if caso['tipo'] == tipo.tipNombre:
                    yCantidadCasosTipo[i] += 1
                    color = "#" + \
                        ''.join([random.choice('0123456789ABCDEF')
                                for j in range(6)])
                    colores.append(color)
            i += 1

        textprops = {"fontsize": 6}
        plt.title("Cantidad de Casos Atendidos \n por Tipo Procedimiento")
        plt.bar(tiposProcedimientos, yCantidadCasosTipo, color=colores)
        rutaImagen = os.path.join(settings.MEDIA_ROOT + "\\" + "grafica3.png")
        plt.savefig(rutaImagen)
        plt.close()
        '''
        return render(request, "administrador/reportesEstadisticos.html")

    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "login.html", {"mensaje": mensaje})


def generarPdfSolicitudes(request):
    from MesaAyuda.pdfSolicitud import Pdf
    solicitudes = Solicitud.objects.all()
    doc = Pdf()
    doc.alias_nb_pages()
    doc.add_page()
    doc.set_font("Arial", "B", 12)
    doc.mostrarDatos(solicitudes)
    doc.output(f'media/solicitudes.pdf')
    return render(request, "administrador/mostrarPdf.html")
    
    

def salir (request):
    auth.logout(request)
    mensaje = "Se ha cerrado sesion"
    return redirect('/')



##### Api



class OficinaAmbienteList(generics.ListCreateAPIView):
    queryset = oficinaAmbiente.objects.all()
    serializer_class = oficinaAmbienteSerializer

class OficinaAmbienteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = oficinaAmbiente.objects.all()
    serializer_class = oficinaAmbienteSerializer