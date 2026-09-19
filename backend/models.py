from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Importamos la clase base que definimos en database.py
from backend.database import Base

# 1. Tabla de Roles (Administrador, Médico, Recepcionista, Enfermero, etc.)
class Rol(Base):
    __tablename__ = "roles" # Nombre exacto de la tabla en Supabase

    id = Column(Integer, primary_key=True, index=True) # Clave primaria autoincrementable
    nombre = Column(String(50), unique=True, nullable=False) # Nombre del rol (único)
    descripcion = Column(String(255), nullable=True) # Descripción opcional

    # Relación de uno a muchos con los usuarios
    usuarios = relationship("Usuario", back_populates="rol")


# 2. Tabla de Usuarios (Credenciales de acceso al sistema)
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True) # Clave primaria
    nombre = Column(String(100), nullable=False) # Nombre completo
    email = Column(String(100), unique=True, nullable=False, index=True) # Correo para login
    password_hash = Column(String(255), nullable=False) # Contraseña encriptada
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False) # Clave foránea que conecta con roles
    activo = Column(Boolean, default=True) # Estado del usuario (activo/inactivo)
    creado_en = Column(DateTime(timezone=True), server_default=func.now()) # Fecha de creación automática

    # Relación para obtener la información del rol asociado
    rol = relationship("Rol", back_populates="usuarios")
    # Relación si el usuario es médico y atiende citas
    citas_medico = relationship("Cita", foreign_keys="Cita.medico_id", back_populates="medico")


# 3. Tabla de Pacientes
class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True) # Clave primaria
    dpi = Column(String(20), unique=True, nullable=True) # Documento de identificación
    nombre = Column(String(100), nullable=False) # Nombres del paciente
    apellido = Column(String(100), nullable=False) # Apellidos del paciente
    telefono = Column(String(20), nullable=True) # Teléfono de contacto
    email = Column(String(100), nullable=True) # Correo electrónico
    direccion = Column(String(255), nullable=True) # Dirección de residencia
    fecha_nacimiento = Column(DateTime, nullable=True) # Fecha de nacimiento
    genero = Column(String(20), nullable=True) # Género
    creado_en = Column(DateTime(timezone=True), server_default=func.now()) # Fecha de registro

    # Relación con las citas médicas del paciente
    citas = relationship("Cita", back_populates="paciente")


# 4. Tabla de Citas Médicas
class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True) # Clave primaria
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False) # ID del paciente
    medico_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False) # ID del médico asignado
    fecha_hora = Column(DateTime, nullable=False) # Fecha y hora programada
    motivo = Column(String(255), nullable=True) # Motivo de la consulta
    estado = Column(String(20), default="Pendiente") # Estado: Pendiente, Completada, Cancelada
    creado_en = Column(DateTime(timezone=True), server_default=func.now()) # Registro automático

    # Relaciones para acceder a los datos completos del paciente y médico
    paciente = relationship("Paciente", back_populates="citas")
    medico = relationship("Usuario", foreign_keys=[medico_id], back_populates="citas_medico")
    consulta = relationship("Consulta", back_populates="cita", uselist=False)


# 5. Tabla de Consultas (Atención médica brindada)
class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True) # Clave primaria
    cita_id = Column(Integer, ForeignKey("citas.id"), nullable=False, unique=True) # Cita correspondiente
    sintomas = Column(Text, nullable=True) # Síntomas reportados
    diagnostico = Column(Text, nullable=False) # Diagnóstico médico
    tratamiento = Column(Text, nullable=True) # Indicaciones de tratamiento
    creado_en = Column(DateTime(timezone=True), server_default=func.now()) # Fecha de registro

    # Relaciones
    cita = relationship("Cita", back_populates="consulta")
    receta = relationship("Receta", back_populates="consulta", uselist=False)


# 6. Tabla de Recetas Médicas
class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True, index=True) # Clave primaria
    consulta_id = Column(Integer, ForeignKey("consultas.id"), nullable=False) # Consulta asociada
    indicaciones = Column(Text, nullable=False) # Indicaciones detalladas de medicamentos
    creado_en = Column(DateTime(timezone=True), server_default=func.now()) # Fecha de emisión

    # Relación con la consulta
    consulta = relationship("Consulta", back_populates="receta")


# 7. Tabla de Inventario de Medicamentos / Insumos
class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(Integer, primary_key=True, index=True) # Clave primaria
    nombre = Column(String(100), nullable=False) # Nombre del producto
    descripcion = Column(String(255), nullable=True) # Descripción técnica o uso
    precio = Column(Numeric(10, 2), nullable=False) # Precio de venta
    stock = Column(Integer, nullable=False, default=0) # Cantidad disponible en inventario


# 8. Tabla de Cobros / Caja
class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True) # Clave primaria
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False) # Paciente a cobrar
    monto_total = Column(Numeric(10, 2), nullable=False) # Total a pagar
    estado = Column(String(20), default="Pendiente") # Estado: Pendiente, Pagado, Anulado
    fecha_emision = Column(DateTime(timezone=True), server_default=func.now()) # Fecha del cobro


# 9. Tabla de Historial Log / Auditoría
class HistorialLog(Base):
    __tablename__ = "historial_logs"

    id = Column(Integer, primary_key=True, index=True) # Clave primaria
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Usuario que realizó la acción
    accion = Column(String(100), nullable=False) # Descripción del evento (ej: "Creó una cita")
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now()) # Fecha y hora exacta