from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

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
    
    # Líder (Puede ser Null al inicio)
    lider_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- RELACIONES ---
    
    # 1. Quién es el líder (Relación con Usuario usando lider_id)
    lider = relationship("Usuario", foreign_keys=[lider_id], back_populates="departamentos_liderados")
    
    # 2. Empleados del depto (Inversa de Usuario.departamento)
    # Al usar back_populates, SQLAlchemy sabe automáticamente que debe usar 'departamento_id' 
    # definido en la clase Usuario. No hace falta poner foreign_keys aquí.
    usuarios = relationship("Usuario", foreign_keys="[Usuario.departamento_id]", back_populates="departamento")
    
    # Otras relaciones
    categorias = relationship("Categoria", back_populates="departamento_rel")
    proyectos = relationship("Proyecto", back_populates="departamento_rel")
    actividades = relationship("Actividad", back_populates="departamento_rel")


# ==========================================
# 3. TABLA: USUARIOS
# ==========================================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    # Nombre de usuario para Login (ej. jtorres)
    user = Column(String(50), unique=True, nullable=False) 
    pass_id = Column(Integer, ForeignKey("passwords.id"), nullable=False)
    
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    
    # ESTE ES EL CAMPO QUE FALTABA EN TU BD
    matricula = Column(String(50), unique=True, nullable=False) 
    
    role = Column(String(50), default="Básico", nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- RELACIONES ---
    
    password = relationship("Password", back_populates="usuario")
    
    # 1. A qué depto pertenece (Usa departamento_id)
    departamento = relationship("Departamento", foreign_keys=[departamento_id], back_populates="usuarios")
    
    # 2. Qué deptos lidera (Inversa de Departamento.lider)
    departamentos_liderados = relationship("Departamento", foreign_keys="[Departamento.lider_id]", back_populates="lider")
    
    proyectos_responsable = relationship("Proyecto", back_populates="responsable_rel")
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

    departamento_rel = relationship("Departamento", back_populates="categorias")
    actividades = relationship("Actividad", back_populates="categoria_rel")


# ==========================================
# 5. TABLA: PROYECTOS
# ==========================================
class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150))
    estado = Column(Integer, default=0, nullable=False)
    
    respondable_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
    
    horainicio = Column(DateTime(timezone=True), nullable=False)
    horacierre = Column(DateTime(timezone=True), nullable=True)
    
    estado = Column(Integer, default=0, nullable=False)
    tipo = Column(Integer, nullable=False)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=True)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usuario_rel = relationship("Usuario", back_populates="actividades")
    categoria_rel = relationship("Categoria", back_populates="actividades")
    departamento_rel = relationship("Departamento", back_populates="actividades")
    proyecto_rel = relationship("Proyecto", back_populates="actividades")