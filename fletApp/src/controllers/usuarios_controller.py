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
# ESCRITURA (CREATE / UPDATE)
# ==========================================

def create_user(nombre: str, apellidos: str, user_id: str, dept_id: int, role: str):
    db: Session = next(get_db())
    try:
        # 1. Validar si el usuario (ID de empleado o username) ya existe
        # Asumimos que 'user_id' es el campo 'user' en la BD (ID de empleado)
        existing = db.query(Usuario).filter(Usuario.user == user_id).first()
        if existing:
             if existing.status == 0:
                # Reactivar
                existing.status = 1
                existing.nombre = nombre
                existing.apellidos = apellidos
                existing.departamento_id = dept_id
                # Mapear rol texto a int
                role_map = {"Básico": 1, "Gerente": 2, "Administrador": 3}
                existing.role = role_map.get(role, 1)
                
                db.commit()
                return {"status": "success", "message": "Usuario reactivado exitosamente."}
             else:
                return {"status": "error", "message": "El ID de usuario ya existe."}

        # 2. Crear Password por defecto
        # TODO: Implementar hash real. Por ahora texto plano o hash dummy.
        new_pass = Password(hash="default_hash_123") 
        db.add(new_pass)
        db.flush() # Para obtener el ID del password

        # 3. Crear Usuario
        role_map = {"Básico": 1, "Gerente": 2, "Administrador": 3}
        role_int = role_map.get(role, 1)

        new_user = Usuario(
            user=user_id,
            pass_id=new_pass.id,
            nombre=nombre,
            apellidos=apellidos,
            role=role_int,
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

def update_user(db_id: int, nombre: str, apellidos: str, user_id: str, dept_id: int, role: str):
    db: Session = next(get_db())
    try:
        user = db.query(Usuario).filter(Usuario.id == db_id).first()
        if not user: return {"status": "error", "message": "Usuario no encontrado"}
        
        # Validar duplicado de user (ID empleado) si cambió
        if user.user != user_id:
            existing = db.query(Usuario).filter(Usuario.user == user_id).first()
            if existing: return {"status": "error", "message": "El ID de usuario ya está en uso."}

        user.nombre = nombre
        user.apellidos = apellidos
        user.user = user_id
        user.departamento_id = dept_id
        
        role_map = {"Básico": 1, "Gerente": 2, "Administrador": 3}
        user.role = role_map.get(role, 1)
        
        db.commit()
        return {"status": "success", "message": "Usuario modificado correctamente."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def delete_user_logical(db_id: int):
    db: Session = next(get_db())
    try:
        user = db.query(Usuario).filter(Usuario.id == db_id).first()
        if not user: return {"status": "error", "message": "No encontrado"}
        
        user.status = 0
        db.commit()
        
        return {"status": "success", "message": "Usuario eliminado correctamente."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
