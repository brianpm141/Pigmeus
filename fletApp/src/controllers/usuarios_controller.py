import bcrypt
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from db.database import get_db
from db.models import Usuario, Password, Departamento, UserRole

# ==========================================
# LECTURA (READ)
# ==========================================

def get_all_users(current_user=None, filter_dept_id=None):
    db: Session = next(get_db())
    try:
        query = db.query(Usuario).options(
            joinedload(Usuario.departamento),
            joinedload(Usuario.password)
        ).filter(Usuario.status == 1)
        
        # Filtrado por Rol
        if current_user:
             # Caso A: Usuario Normal (Restringido a su depto si no es Admin/Gerente? El prompt no especifica restricción cruzada)
             # Para colaboradores, asumimos que se puede colaborar con cualquiera.
             # Pero mantenemos la lógica base:
             if hasattr(current_user, 'role'):
                 role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
                 
                 # Si se pasa un filtro explicito, lo usamos (útil para dropdowns dinámicos)
                 if filter_dept_id:
                     query = query.filter(Usuario.departamento_id == int(filter_dept_id))
                 
                 # Si NO hay filtro explicito y NO es Admin/Gerente, restringir (comportamiento default anterior)
                 elif "Administrador" not in role_str and "Gerente" not in role_str:
                     # Nota: Si queremos permitir ver todos para colaborar, quitamos esto o lo ajustamos.
                     # Por ahora, si no pasan filtro, filtra por su depto.
                     query = query.filter(Usuario.departamento_id == current_user.departamento_id)
            
             # Caso B: Departamento (Invitado)
             elif hasattr(current_user, 'code'):
                 query = query.filter(Usuario.departamento_id == current_user.id)
        
        # Si no hay current_user (llamada interna sin auth context?), o si se paso filter_dept_id sin current_user
        elif filter_dept_id:
             query = query.filter(Usuario.departamento_id == int(filter_dept_id))
        
        users = query.order_by(Usuario.nombre.asc()).all()
        
        return users
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        db.close()

# ==========================================
# ESCRITURA (CREATE)
# ==========================================

def create_user(username: str, raw_password: str, nombre: str, apellidos: str, matricula: str, role: str, dept_id: int):
    db: Session = next(get_db())
    try:
        # 1. Validaciones de Integridad (Duplicados)
        
        # A) Validar Username (Login)
        if db.query(Usuario).filter(Usuario.username == username).first():
            return {"status": "error", "message": "El nombre de usuario (Login) ya está ocupado."}
        
        # B) Validar Matrícula (ID Empleado)
        existing_mat = db.query(Usuario).filter(Usuario.matricula == matricula).first()
        if existing_mat:
            # Lógica de Reactivación (Si estaba borrado)
            if existing_mat.status == 0:
                # Nota: Para reactivar, requeriríamos lógica extra para el password/username
                # Por seguridad, mejor pedimos usar otra matrícula o contactar soporte.
                return {"status": "error", "message": "Esa matrícula pertenece a un usuario dado de baja."}
            return {"status": "error", "message": "Esa matrícula ya está registrada."}

        # 2. Encriptar Contraseña
        hashed_bytes = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed_bytes.decode('utf-8')

        # 3. Guardar Password
        new_pass = Password(hash=hashed_str)
        db.add(new_pass)
        db.flush() # Obtenemos ID

        # 4. Crear Usuario
        # Convertimos string a Enum si es necesario, aunque SQLAlchemy suele manejar strings si coinciden con los valores del Enum
        # Pero para ser explícitos y seguros:
        try:
            role_enum = UserRole(role)
        except ValueError:
            # Si el string no coincide con ningún valor del Enum, fallback a Básico o error
            role_enum = UserRole.BASICO

        new_user = Usuario(
            username=username, # Corregido: models.py usa 'username', no 'user'
            pass_id=new_pass.id,
            nombre=nombre,
            apellidos=apellidos,
            matricula=matricula,
            role=role_enum, 
            departamento_id=dept_id,
            status=1
        )
        
        db.add(new_user)
        db.commit()
        
        return {"status": "success", "message": "Usuario creado correctamente."}
        
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"Error en BD: {str(e)}"}
    finally:
        db.close()

# ==========================================
# ACTUALIZACIÓN (UPDATE)
# ==========================================

def update_user(db_id: int, nombre: str, apellidos: str, matricula: str, role: str, dept_id: int):
    """
    Nota: Esta función actualiza datos personales. 
    NO actualiza contraseña ni username por seguridad.
    """
    db: Session = next(get_db())
    try:
        user = db.query(Usuario).filter(Usuario.id == db_id).first()
        if not user: return {"status": "error", "message": "Usuario no encontrado"}
        
        # Validar que la nueva matrícula no pertenezca a OTRO usuario
        existing_mat = db.query(Usuario).filter(
            Usuario.matricula == matricula, 
            Usuario.id != db_id # Excluirse a sí mismo
        ).first()
        
        if existing_mat: 
            return {"status": "error", "message": "La matrícula ya pertenece a otro usuario."}

        # Actualizar campos
        user.nombre = nombre
        user.apellidos = apellidos
        user.matricula = matricula
        
        try:
            role_enum = UserRole(role)
        except ValueError:
            role_enum = UserRole.BASICO
            
        user.role = role_enum
        user.departamento_id = dept_id
        
        db.commit()
        return {"status": "success", "message": "Usuario modificado correctamente."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# ==========================================
# ELIMINACIÓN (DELETE)
# ==========================================

def delete_user_logical(db_id: int):
    db: Session = next(get_db())
    try:
        user = db.query(Usuario).filter(Usuario.id == db_id).first()
        if not user: return {"status": "error", "message": "No encontrado"}
        
        user.status = 0
        db.commit()
        
        return {"status": "success", "message": "Usuario dado de baja."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# ==========================================
# AUTHENTICATION
# ==========================================

def login_user(username: str, password_raw: str):
    db: Session = next(get_db())
    try:
        # 1. Buscar usuario
        user = db.query(Usuario).options(
            joinedload(Usuario.password),
            joinedload(Usuario.departamento)
        ).filter(Usuario.username == username).first()
        
        if not user:
            return {"status": "error", "message": "Usuario no encontrado."}
        
        if user.status == 0:
            return {"status": "error", "message": "Cuenta inactiva."}

        # 2. Verificar Password
        if not user.password:
            # Caso raro: usuario sin pass_id o registro roto
            return {"status": "error", "message": "Error de integridad: Sin credenciales."}

        stored_hash = user.password.hash.encode('utf-8')
        if bcrypt.checkpw(password_raw.encode('utf-8'), stored_hash):
            return {"status": "success", "user": user, "message": "Bienvenido"}
        else:
            return {"status": "error", "message": "Contraseña incorrecta."}

    except Exception as e:
        return {"status": "error", "message": f"Error de sistema: {str(e)}"}
    finally:
        db.close()