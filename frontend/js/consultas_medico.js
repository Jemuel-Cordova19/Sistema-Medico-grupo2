document.addEventListener("DOMContentLoaded", () => {
    // 1. Obtener el id_cita de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const idCita = urlParams.get('id_cita');
    
    console.log("ID de cita recibido para la consulta:", idCita);

    const spanCita = document.getElementById('id-cita-txt');
    if (spanCita) {
        spanCita.innerText = idCita || "--";
    }

    // 2. Manejar el envío del formulario
    const formConsulta = document.getElementById('form-consulta');
    if (formConsulta) {
        formConsulta.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Recopilar todos los datos requeridos por el cliente
            const datosConsulta = {
                id_cita: parseInt(idCita),
                // Signos Vitales
                presion_arterial: document.getElementById('presion')?.value || "",
                temperatura: parseFloat(document.getElementById('temperatura')?.value || 0),
                peso: parseFloat(document.getElementById('peso')?.value || 0),
                frecuencia_cardiaca: parseInt(document.getElementById('frecuencia_cardiaca')?.value || 0),
                
                // Historia Clínica y Diagnóstico
                motivo_consulta: document.getElementById('motivo_consulta')?.value || "",
                sintomas: document.getElementById('sintomas')?.value || "",
                antecedentes: document.getElementById('antecedentes')?.value || "",
                alergias: document.getElementById('alergias')?.value || "",
                diagnostico: document.getElementById('diagnostico')?.value || "",
                observaciones: document.getElementById('observaciones')?.value || "",

                // Receta Médica
                medicamento: document.getElementById('medicamento')?.value || "",
                presentacion: document.getElementById('presentacion')?.value || "",
                dosis: document.getElementById('dosis')?.value || "",
                frecuencia: document.getElementById('frecuencia')?.value || "",
                duracion: document.getElementById('duracion')?.value || "",
                indicaciones_adicionales: document.getElementById('indicaciones')?.value || ""
            };

            try {
                const response = await fetch('http://127.0.0.1:8000/medico/guardar-consulta', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(datosConsulta)
                });

                if (response.ok) {
                    alert('¡Consulta registrada con éxito y cita marcada como Atendida!');
                    window.location.href = 'medico_panel.html';
                } else {
                    const errorData = await response.json();
                    alert(`Error al guardar la consulta: ${errorData.detail || 'Ocurrió un error inesperado'}`);
                }
            } catch (error) {
                console.error('Error de conexión con el servidor:', error);
                alert('No se pudo conectar con el servidor backend.');
            }
        });
    }
});
// Verificar si la URL trae el parámetro para imprimir automáticamente
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('imprimir') === 'true') {
        // Esperamos 1 segundo a que los datos de la consulta carguen en pantalla y lanzamos la impresión
        setTimeout(() => {
            window.print();
        }, 1000);
    }
});