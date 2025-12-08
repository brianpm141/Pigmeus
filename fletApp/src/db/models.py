import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

# ==========================================
# 0. ENUMS
# ==========================================
# Definimos el Enum en Python para asegurar consistencia
class UserRole(enum.Enum):
    BASICO = "Básico"
    GERENTE = "Gerente"
    ADMIN = "Administrador"

# ==========================================
# 1. TABLA: PASSWORDS
# ==========================================
class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String(255), nullable=False)

    # Relación 1-1
    usuario = relationship("Usuario", back_populates="password", uselist=False)


# ==========================================
# 2. TABLA: DEPARTAMENTOS
# ==========================================
class Departamento(Base):
    __tablename__ = "departamentos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    code = Column(Integer, nullable=False)
    
    status = Column(Integer, default=1, comment="1=Activo, 0=Baja")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- RELACIONES ---
    
    # 1. Empleados del depto (Inversa de Usuario.departamento)
    usuarios = relationship("Usuario", back_populates="departamento")
    
    # 2. Categorías del depto
    categorias = relationship("Categoria", back_populates="departamento_rel")
    
    # 3. Proyectos del depto
    proyectos = relationship("Proyecto", back_populates="departamento_rel")

    # Nota: Ya NO hay relación directa con 'actividades' (se hace a través de usuarios)


# ==========================================
# 3. TABLA: USUARIOS
# ==========================================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    # Cambiado de 'user' a 'username' para coincidir con el diagrama
    username = Column(String(30), unique=True, nullable=False) 
    pass_id = Column(Integer, ForeignKey("passwords.id"), nullable=False)
    
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    matricula = Column(String(50), unique=True, nullable=False) 
    
    # USO DEL ENUM
    role = Column(Enum(UserRole), default=UserRole.BASICO, nullable=False)
    
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- RELACIONES ---
    
    password = relationship("Password", back_populates="usuario")
    
    # Relación con Departamento
    departamento = relationship("Departamento", back_populates="usuarios")
    
    # Proyectos donde es responsable
    proyectos_responsable = relationship("Proyecto", back_populates="responsable_rel")
    
    # Actividades que creó el usuario
    actividades = relationship("Actividad", back_populates="usuario_rel")


# ==========================================
# 4. TABLA: CATEGORIAS
# ==========================================
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- RELACIONES ---
    departamento_rel = relationship("Departamento", back_populates="categorias")
    actividades = relationship("Actividad", back_populates="categoria_rel")


# ==========================================
# 5. TABLA: PROYECTOS
# ==========================================
class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    # Agregado nullable=False
    nombre = Column(String(100), nullable=False) 
    estado = Column(Integer, default=0, nullable=False, comment="0=Pendiente, 1=Proceso, 2=Terminado")
    descripcion = Column(String(180), nullable=True)

    # Corregido typo: respondable_id -> responsable_id
    responsable_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    
    status = Column(Integer, default=1)
    
    # Fechas agregadas según diagrama
    fecha_est = Column(DateTime(timezone=True), nullable=True)
    fecha_mov = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- RELACIONES ---
    responsable_rel = relationship("Usuario", back_populates="proyectos_responsable")
    departamento_rel = relationship("Departamento", back_populates="proyectos")
    actividades = relationship("Actividad", back_populates="proyecto_rel")


# ==========================================
# 6. TABLA: ACTIVIDADES
# ==========================================
class Actividad(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    
    # DateTime(timezone=True) equivale a timestamptz en Postgres
    horainicio = Column(DateTime(timezone=True), nullable=False)
    horacierre = Column(DateTime(timezone=True), nullable=True)
    
    estado = Column(Integer, default=0, nullable=False, comment="0=Pendiente, 1=Completa")
    tipo = Column(Integer, nullable=False, comment="0=General, 1=De Proyecto")
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    
    # ELIMINADO: departamento_id (Redundante, se obtiene via usuario_id)
    
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=True)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- RELACIONES ---
    usuario_rel = relationship("Usuario", back_populates="actividades")
    categoria_rel = relationship("Categoria", back_populates="actividades")
    proyecto_rel = relationship("Proyecto", back_populates="actividades")
    
    # ELIMINADO: departamento_rel