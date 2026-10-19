document.addEventListener("DOMContentLoaded", () => {
    const sesionGuardada = localStorage.getItem("usuario_session");
    
    // IMPRIMIMOS EN CONSOLA LO QUE TIENE EL NAVEGADOR
    console.log("VALOR EN LOCALSTORAGE:", sesionGuardada);

    if (!sesionGuardada) {
        console.warn("¡No hay sesión! Pausando redirección para ver el error.");
        
        // COMENTAMOS ESTA LÍNEA TEMPORALMENTE PARA QUE NO TE BOTE:
        // window.location.href = "../index.html";
        return;
    }

    const sesion = JSON.parse(sesionGuardada);
    console.log("OBJETO SESION PARSEADO:", sesion);

    // Soporta tanto si el usuario viene anidado como si está en la raíz
    const usuario = sesion.usuario || sesion;

    // 1. Mostrar el nombre real de la doctora o doctor
    const elementoNombre = document.getElementById("nombre_medico");
    if (elementoNombre) {
        const nombre = usuario.nombre || usuario.nombre_usuario || usuario.username || "Médico";
        const apellido = usuario.apellido || usuario.apellido_usuario || "";
        elementoNombre.textContent = `Dr. ${nombre} ${apellido}`.trim();
    }

    // 2. Configurar botón de cerrar sesión
    const botonCerrarSesion = document.getElementById("cerrar_sesion");
    if (botonCerrarSesion) {
        botonCerrarSesion.addEventListener("click", (e) => {
            e.preventDefault();
            localStorage.removeItem("usuario_session");
            window.location.href = "../index.html";
        });
    }

    // 3. Extraer el ID del médico con total seguridad y cargar citas
    // Extraemos el ID de usuario de la sesión
    const userId = usuario.id || usuario.id_usuario || 3;
    
    // Mapeo exacto según tu base de datos en Supabase:
    // Si el usuario es el ID 3 (Dra. María Mercedes), su ID en la tabla medicos es 1.
    // Si es otro usuario, usa su propio ID.
    const medicoId = (userId === 3) ? 1 : userId;
    
    console.log("ID DE MÉDICO USADO PARA CONSULTAR CITAS:", medicoId);
    cargarCitasMedico(medicoId);
});

async function cargarCitasMedico(idMedico) {
    const tabla = document.getElementById("tabla_citas");
    if (!tabla) return;

    try {
        console.log(`Solicitando citas al backend para el médico ID: ${idMedico}`);
        const respuesta = await fetch(`http://127.0.0.1:8000/medico/citas/${idMedico}`);
        
        if (respuesta.ok) {
            const citas = await respuesta.json();
            console.log("CITAS CRUDAS RECIBIDAS DEL BACKEND:", citas);
            
            if (!citas || citas.length === 0) {
                tabla.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 15px;">No hay citas asignadas para este médico en la base de datos.</td></tr>`;
                return;
            }

            // Limpiamos la tabla y pintamos las citas de forma flexible
            // Limpiamos la tabla y pintamos las citas con sus botones de acción
            tabla.innerHTML = "";
            citas.forEach(cita => {
                const hora = cita.hora || cita.fecha_hora || 'N/D';
                const paciente = cita.paciente || cita.nombre_paciente || 'Paciente Asignado';
                const motivo = cita.motivo || cita.motivo_consulta || 'Sin motivo registrado';
                const estado = cita.estado || cita.status || 'Pendiente';
                const idCita = cita.id_cita || cita.id || 1;

                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td>${hora}</td>
                    <td>${paciente}</td>
                    <td>${motivo}</td>
                    <td><span style="color: #007bff; font-weight: bold;">${estado}</span></td>
                    <td>
                        <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                            <a href="consultas_medico.html?id_cita=${idCita}" class="btn-primary" style="padding: 5px 8px; text-decoration: none; background: #007bff; color: white; border-radius: 4px; font-size: 12px;">Atender</a>
                            <button onclick="generarPDF(${idCita})" style="padding: 5px 8px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">PDF</button>
                        </div>
                    </td>
                `;
                tabla.appendChild(fila);
            });
        } else {
            console.error("Error al obtener citas del servidor:", respuesta.status);
            tabla.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red; padding: 15px;">Error al cargar las citas (Código ${respuesta.status}).</td></tr>`;
        }
    } catch (error) {
        console.error("Error de conexión:", error);
        tabla.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red; padding: 15px;">No se pudo conectar con el servidor backend.</td></tr>`;
    }
}

function verHistorial(paciente_id) {
    if (!paciente_id) {
        alert("ID de paciente no válido.");
        return;
    }
    window.location.href = `historial_paciente.html?paciente_id=${paciente_id}`;
}
function generarPDF(idCita) {
    console.log(`Generando reporte para la cita ID: ${idCita}`);
    
    // Abre una ventana limpia con la información o redirige a la vista de atención para imprimir
    window.open(`consultas_medico.html?id_cita=${idCita}&imprimir=true`, '_blank');
}