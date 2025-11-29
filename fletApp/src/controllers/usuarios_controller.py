import bcrypt
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from db.database import get_db
from db.models import Usuario, Password, Departamento

# ==========================================
# LECTURA (READ)
# ==========================================

def get_all_users():
    db: Session = next(get_db())
    try:
        users = db.query(Usuario).options(
            joinedload(Usuario.departamento),
            joinedload(Usuario.password)
        ).filter(
            Usuario.status == 1
        ).order_by(Usuario.nombre.asc()).all()
        
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
        if db.query(Usuario).filter(Usuario.user == username).first():
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
        # CORRECCIÓN: No mapeamos rol a int, lo guardamos como string directo
        new_user = Usuario(
            user=username,
            pass_id=new_pass.id,
            nombre=nombre,
            apellidos=apellidos,
            matricula=matricula,
            role=role, 
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
        user.role = role # Guardamos string directo
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