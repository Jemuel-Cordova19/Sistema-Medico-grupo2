document.addEventListener("DOMContentLoaded", () => {
    // 1. Selección de elementos del formulario
    const formulario = document.querySelector("form");
    const campoUsuario = document.getElementById("correo_o_usuario") || document.querySelector("input[type='text']");
    const campoContrasena = document.getElementById("contrasena") || document.querySelector("input[type='password']");
    
    // Contenedor del mensaje de error
    const contenedorError = document.getElementById("mensaje_error") || 
                            document.querySelector(".error-message") || 
                            document.querySelector("[id*='error']");

    // Botón o texto para mostrar/ocultar contraseña
    const botonTogglePassword = document.getElementById("toggle_password") || 
                                document.querySelector(".toggle-password") || 
                                Array.from(document.querySelectorAll("button, span, a")).find(
                                    el => el.textContent.trim().toLowerCase() === "mostrar" || el.textContent.trim().toLowerCase() === "ocultar"
                                );

    // -------------------------------------------------------------
    // FUNCIONALIDAD 1: Mostrar / Ocultar Contraseña
    // -------------------------------------------------------------
    if (botonTogglePassword && campoContrasena) {
        botonTogglePassword.addEventListener("click", (e) => {
            e.preventDefault();
            
            const esPassword = campoContrasena.getAttribute("type") === "password";
            campoContrasena.setAttribute("type", esPassword ? "text" : "password");
            
            botonTogglePassword.textContent = esPassword ? "Ocultar" : "Mostrar";
        });
    }

    // -------------------------------------------------------------
    // FUNCIONALIDAD 2: Procesar Login y Guardar Sesión
    // -------------------------------------------------------------
    if (formulario) {
        formulario.addEventListener("submit", async function(evento) {
            evento.preventDefault();

            if (contenedorError) {
                contenedorError.textContent = "";
                contenedorError.style.display = "none";
            }

            const valorUsuario = campoUsuario ? campoUsuario.value.trim() : "";
            const valorContrasena = campoContrasena ? campoContrasena.value.trim() : "";

            if (!valorUsuario || !valorContrasena) {
                mostrarMensajeError("Por favor, ingrese usuario y contraseña.");
                return;
            }

            const datosAEnviar = {
                correo_electronico_usuario: valorUsuario,
                contrasena_usuario: valorContrasena
            };

            try {
                const respuestaServidor = await fetch("http://127.0.0.1:8000/autenticacion/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(datosAEnviar)
                });

                const datosRespuesta = await respuestaServidor.json();

                if (respuestaServidor.ok) {
                    const rolAsignado = datosRespuesta.identificador_rol_usuario;

                    // NUEVA LÍNEA AGREGADA: Guardar datos del usuario en la memoria del navegador
                    localStorage.setItem("usuario_session", JSON.stringify(datosRespuesta));

                    if (rolAsignado === 1) {
                    window.location.href = "admin/admin_jimena.html";
                    } else if (rolAsignado === 2) {
                    window.location.href = "medico/medico_panel.html";
                    } else if (rolAsignado === 3) {
                    window.location.href = "recepcion/recepcion_melissa.html";
                    } else {
                    mostrarMensajeError("Error: Rol de usuario desconocido.");
                    }
                } else {
                    const mensajeBackend = datosRespuesta.detail || "Usuario o contraseña incorrectos.";
                    mostrarMensajeError(mensajeBackend);
                }
            } catch (error) {
                mostrarMensajeError("Error de conexión con el servidor. Verifique que el backend esté ejecutándose.");
            }
        });
    }

    function mostrarMensajeError(mensaje) {
        if (contenedorError) {
            contenedorError.textContent = mensaje;
            contenedorError.style.display = "block";
            contenedorError.style.color = "#d9534f";
        } else {
            alert(mensaje);
        }
    }
});