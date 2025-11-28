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
    hash = Column(String(255), nullable=False) # Guardamos el hash encriptado

    # Relación inversa (para acceder desde el password al usuario si fuera necesario)
    usuario = relationship("Usuario", back_populates="password", uselist=False)


# ==========================================
# 2. TABLA: DEPARTAMENTOS
# ==========================================
class Departamento(Base):
    __tablename__ = "departamentos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    
    # Lider: Puede ser NULL porque al crear el depto quizás aun no asignas jefe
    lider_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    status = Column(Integer, default=1) # 1=Activo, 0=Baja Lógica
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    # Usamos foreign_keys para distinguir esta relación de la de "empleados del depto"
    lider = relationship("Usuario", foreign_keys=[lider_id], back_populates="departamentos_liderados")
    
    # Lista de todos los usuarios que pertenecen a este departamento
    usuarios = relationship("Usuario", foreign_keys="[Usuario.departamento_id]", back_populates="departamento")
    
    categorias = relationship("Categoria", back_populates="departamento_rel")
    proyectos = relationship("Proyecto", back_populates="departamento_rel")
    actividades = relationship("Actividad", back_populates="departamento_rel")


# ==========================================
# 3. TABLA: USUARIOS
# ==========================================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(50), unique=True, nullable=False)
    
    # Password: 1 a 1 obligatoria
    pass_id = Column(Integer, ForeignKey("passwords.id"), nullable=False)
    
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    
    # Rol: 1=Básico, 2=Gerente, 3=Admin (por defecto 1)
    role = Column(Integer, default=1, nullable=False)
    
    # Departamento: OBLIGATORIO (nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ------------------ Relaciones ------------------
    password = relationship("Password", back_populates="usuario")
    
    # Relación principal: A qué depto pertenece
    departamento = relationship("Departamento", foreign_keys=[departamento_id], back_populates="usuarios")
    
    # Relación secundaria: Qué deptos lidera (puede ser una lista vacía)
    departamentos_liderados = relationship("Departamento", foreign_keys=[Departamento.lider_id], back_populates="lider")
    
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

    # ------------------ Relaciones ------------------
    departamento_rel = relationship("Departamento", back_populates="categorias")
    actividades = relationship("Actividad", back_populates="categoria_rel")


# ==========================================
# 5. TABLA: PROYECTOS
# ==========================================
class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150))
    
    # Estado del proyecto: 0=Pendiente, 1=Proceso, 2=Terminado
    estado = Column(Integer, default=0, nullable=False)
    
    respondable_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ------------------ Relaciones ------------------
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
    
    # DateTime guarda Fecha Y Hora
    horainicio = Column(DateTime(timezone=True), nullable=False)
    horacierre = Column(DateTime(timezone=True), nullable=True)
    
    # Estado: 0=Pendiente, 1=Completa
    estado = Column(Integer, default=0, nullable=False)
    
    # Tipo: 0=General, 1=De Proyecto
    tipo = Column(Integer, nullable=False)
    
    # Claves Foráneas
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    
    # Puede ser nulo si es una actividad general (tipo 0)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=True)
    
    status = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ------------------ Relaciones ------------------
    usuario_rel = relationship("Usuario", back_populates="actividades")
    categoria_rel = relationship("Categoria", back_populates="actividades")
    departamento_rel = relationship("Departamento", back_populates="actividades")
    proyecto_rel = relationship("Proyecto", back_populates="actividades")