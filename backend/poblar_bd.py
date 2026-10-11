# Archivo: backend/poblar_bd.py
# Script inteligente definitivo: reutiliza o crea usuarios para médicos sin conflictos de llave única

from sqlalchemy import text
from database import SessionLocal
from datetime import datetime, timedelta
import random

def obtener_columnas(db, tabla):
    try:
        res = db.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{tabla}';"))
        return [row[0] for row in res]
    except Exception:
        return []

def contar_registros(db, tabla):
    try:
        res = db.execute(text(f"SELECT COUNT(*) FROM {tabla};"))
        row = res.fetchone()
        return row[0] if row else 0
    except Exception:
        return 0

def poblar_base_datos():
    db = SessionLocal()
    print("🚀 Verificando base de datos para completar registros faltantes...")

    try:
        cols_user = obtener_columnas(db, 'usuarios')
        cols_med = obtener_columnas(db, 'medicos')
        cols_pac = obtener_columnas(db, 'pacientes')
        cols_rec = obtener_columnas(db, 'recetas')

        # 1. Médicos y sus Usuarios (Meta: 3 médicos con sus respectivos usuarios)
        count_med = contar_registros(db, 'medicos')
        if count_med < 3:
            faltan_med = 3 - count_med
            print(f"Actuales en 'medicos': {count_med}. Faltan {faltan_med} para completar 3...")
            
            # Obtener usuario_ids ya usados en medicos para evitar UniqueViolation
            res_used_u = db.execute(text("SELECT usuario_id FROM medicos WHERE usuario_id IS NOT NULL;"))
            used_user_ids = [r[0] for r in res_used_u.fetchall()]

            # Obtener todos los usuarios existentes
            res_u = db.execute(text("SELECT id FROM usuarios;"))
            all_users = [r[0] for r in res_u.fetchall()]

            medicos_data = [
                ("MED-2002", "Dra. Jimena Morales", "Pediatría", "jimena.morales@clinica.com", "COL-1002", "5550-1002", "08:00 - 16:00"),
                ("MED-2003", "Dr. Roberto Gómez", "Cardiología", "roberto.gomez@clinica.com", "COL-1003", "5550-1003", "09:00 - 17:00")
            ]
            
            for idx, (codigo, nombre, esp, corr, colegiado, tel, horario) in enumerate(medicos_data[:faltan_med], start=count_med+1):
                try:
                    # Buscar un usuario libre que no esté asignado a ningún médico
                    libre_users = [uid for uid in all_users if uid not in used_user_ids]
                    
                    if libre_users:
                        nuevo_usuario_id = libre_users[0]
                        used_user_ids.append(nuevo_usuario_id)
                    else:
                        # Si no hay usuarios libres, creamos uno nuevo
                        user_data = {}
                        if 'nombre' in cols_user: user_data['nombre'] = nombre
                        elif 'nombre_completo' in cols_user: user_data['nombre_completo'] = nombre
                        if 'correo' in cols_user: user_data['correo'] = corr
                        if 'email' in cols_user: user_data['email'] = corr
                        if 'password' in cols_user: user_data['password'] = "123456"
                        if 'rol' in cols_user: user_data['rol'] = "medico"
                        elif 'tipo' in cols_user: user_data['tipo'] = "medico"

                        u_keys = list(user_data.keys())
                        u_vals = [f":{k}" for k in u_keys]
                        sql_user = f"INSERT INTO usuarios ({', '.join(u_keys)}) VALUES ({', '.join(u_vals)}) RETURNING id;"
                        
                        res_uid = db.execute(text(sql_user), user_data)
                        nuevo_usuario_id = res_uid.fetchone()[0]
                        used_user_ids.append(nuevo_usuario_id)

                    # Insertar el médico enlazado al usuario disponible/nuevo
                    data = {}
                    if 'codigo_interno' in cols_med: data['codigo_interno'] = codigo
                    if 'nombre_completo' in cols_med: data['nombre_completo'] = nombre
                    elif 'nombre' in cols_med: data['nombre'] = nombre
                    elif 'nombres' in cols_med: data['nombres'] = nombre
                    
                    if 'especialidad' in cols_med: data['especialidad'] = esp
                    if 'correo' in cols_med: data['correo'] = corr
                    if 'colegiado' in cols_med: data['colegiado'] = colegiado
                    if 'telefono' in cols_med: data['telefono'] = tel
                    if 'horario_atencion' in cols_med: data['horario_atencion'] = horario
                    if 'usuario_id' in cols_med: data['usuario_id'] = nuevo_usuario_id

                    keys = list(data.keys())
                    vals = [f":{k}" for k in keys]
                    sql_med = f"INSERT INTO medicos ({', '.join(keys)}) VALUES ({', '.join(vals)});"
                    db.execute(text(sql_med), data)
                    db.commit()
                    print(f"✅ Médico {idx} insertado con éxito.")
                except Exception as e:
                    db.rollback()
                    print(f"❌ Error al insertar médico {idx}: {e}")
        else:
            print("✔️ Tabla 'medicos' ya cuenta con los registros necesarios.")

        # 2. Pacientes (Meta: 10 pacientes)
        count_pac = contar_registros(db, 'pacientes')
        if count_pac < 10:
            faltan_pac = 10 - count_pac
            print(f"Actuales en 'pacientes': {count_pac}. Faltan {faltan_pac} para completar 10...")
            pacientes_restantes = [
                ("Carlos", "Ruiz", "5553-0003", "Zona 1, Ciudad", "Masculino", "5550-9003", "5550-8003", "2501123450103"),
                ("Ana", "Gómez", "5554-0004", "Zona 4, Mixco", "Femenino", "5550-9004", "5550-8004", "2501123450104"),
                ("Luis", "Torres", "5555-0005", "Zona 9, Capital", "Masculino", "5550-9005", "5550-8005", "2501123450105"),
                ("Sofía", "Martínez", "5556-0006", "San Lucas Sac.", "Femenino", "5550-9006", "5550-8006", "2501123450106"),
                ("Pedro", "Ramírez", "5557-0007", "Antigua Guatemala", "Masculino", "5550-9007", "5550-8007", "2501123450107"),
                ("Lucía", "Fernández", "5558-0008", "Villa Nueva", "Femenino", "5550-9008", "5550-8008", "2501123450108"),
                ("Jorge", "Castillo", "5559-0009", "Chinautla", "Masculino", "5550-9009", "5550-8009", "2501123450109"),
                ("Elena", "Vargas", "5550-0010", "Amatitlán", "Femenino", "5550-9010", "5550-8010", "2501123450110")
            ]
            for idx, (nombres, apellidos, telefono, direccion, sexo, contacto, tel_emergencia, dpi) in enumerate(pacientes_restantes[:faltan_pac], start=count_pac+1):
                try:
                    data = {}
                    if 'codigo_interno' in cols_pac: data['codigo_interno'] = f"PAC-20{idx:02d}"
                    if 'nombres' in cols_pac: data['nombres'] = nombres
                    if 'apellidos' in cols_pac: data['apellidos'] = apellidos
                    if 'telefono' in cols_pac: data['telefono'] = telefono
                    if 'direccion' in cols_pac: data['direccion'] = direccion
                    if 'fecha_nacimiento' in cols_pac: data['fecha_nacimiento'] = datetime(1990, 5, 12)
                    if 'sexo' in cols_pac: data['sexo'] = sexo
                    if 'contacto_emergencia' in cols_pac: data['contacto_emergencia'] = contacto
                    if 'telefono_emergencia' in cols_pac: data['telefono_emergencia'] = tel_emergencia
                    
                    for c in cols_pac:
                        if c in ['dpi', 'documento', 'identificacion']:
                            data[c] = dpi

                    keys = list(data.keys())
                    vals = [f":{k}" for k in keys]
                    sql = f"INSERT INTO pacientes ({', '.join(keys)}) VALUES ({', '.join(vals)});"
                    db.execute(text(sql), data)
                    db.commit()
                    print(f"✅ Paciente {idx} insertado con éxito.")
                except Exception as e:
                    db.rollback()
                    print(f"❌ Error al insertar paciente {idx}: {e}")
        else:
            print("✔️ Tabla 'pacientes' ya cuenta con los registros necesarios.")

        # 3. Recetas (Meta: 5 recetas)
        count_rec = contar_registros(db, 'recetas')
        res_co = db.execute(text("SELECT id FROM consultas;"))
        consulta_ids = [r[0] for r in res_co.fetchall()]

        if count_rec < 5 and consulta_ids:
            faltan_rec = 5 - count_rec
            print(f"Actuales en 'recetas': {count_rec}. Faltan {faltan_rec} para completar 5...")
            
            # Obtener pacientes y medicos actuales
            res_p = db.execute(text("SELECT id FROM pacientes;"))
            paciente_ids = [r[0] for r in res_p.fetchall()]
            res_m = db.execute(text("SELECT id FROM medicos;"))
            medico_ids = [r[0] for r in res_m.fetchall()]
            
            if paciente_ids and medico_ids:
                for i in range(1, faltan_rec + 1):
                    con_id = consulta_ids[(count_rec + i - 1) % len(consulta_ids)]
                    p_id = random.choice(paciente_ids)
                    m_id = random.choice(medico_ids)
                    
                    data = {
                        "paciente_id": p_id,
                        "medico_id": m_id,
                        "consulta_id": con_id,
                        "fecha": datetime.now() - timedelta(days=i)
                    }
                    
                    if 'medicamento' in cols_rec: data['medicamento'] = "Ibuprofeno 600mg"
                    if 'dosis' in cols_rec: data['dosis'] = "1 tableta"
                    if 'frecuencia' in cols_rec: data['frecuencia'] = "Cada 8 horas"
                    
                    for c in cols_rec:
                        if c in ['duracion', 'tiempo', 'plazo']:
                            data[c] = "5 días"
                        if c in ['detalle', 'descripcion', 'indicaciones', 'contenido', 'observaciones', 'receta', 'texto']:
                            data[c] = "Tomar con alimentos"

                    filtered_data = {k: v for k, v in data.items() if k in cols_rec}
                    keys = list(filtered_data.keys())
                    vals = [f":{k}" for k in keys]
                    sql = f"INSERT INTO recetas ({', '.join(keys)}) VALUES ({', '.join(vals)});"
                    try:
                        db.execute(text(sql), filtered_data)
                        db.commit()
                        print(f"✅ Receta {i} insertada con éxito.")
                    except Exception as e:
                        db.rollback()
                        print(f"❌ Error al insertar receta {i}: {e}")
        else:
            print("✔️ Tabla 'recetas' ya cuenta con los registros necesarios.")

        print("¡Proceso de completado finalizado exitosamente!")

    except Exception as e:
        db.rollback()
        print("❌ Error general:", e)
    finally:
        db.close()

if __name__ == "__main__":
    poblar_base_datos()