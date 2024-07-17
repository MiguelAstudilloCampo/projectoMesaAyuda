// function listarTecnicos() {
//   let url = "/listarTecnicos/";
//   fetch(url, {
//     method: "GET",
//     headers: {
//       "Content-Type": "application/json",
//     },
//   })
//   .then((respuesta) => respuesta.json())
//   .then
// }

function agregarIdCaso(id) {
  document.getElementById("idCaso").value = id;
}

function mostrarImagen (evento){
  const archivos = evento.target.files
  const imagen = archivos[0]
  const url = URL.createObjectURL(imagen)
  const img = document.getElementById('imagenMostrar')
  img.setAttribute('src',url)
}

let tecnicos = []


function cambiarRol() {
    const rol = document.getElementById('cbRolMenu')
    console.log(rol.value)
    if (rol.value == "Tecnico") {
        location.href = "/inicioTecnico/"
    }
    if (rol.value == "Administrador") {
        location.href = "/inicioAdministrador/"
    }
    if (rol.value == "Empleado") {
        location.href = "/inicioEmpleado/"
    }
}