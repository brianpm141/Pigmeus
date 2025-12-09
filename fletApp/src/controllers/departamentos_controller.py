from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from db.database import get_db
from db.models import Departamento, Usuario

# ==========================================
# LECTURA (READ)
# ==========================================

def get_all_departments():
    db: Session = next(get_db())
    try:
        depts = db.query(Departamento).options(
            joinedload(Departamento.usuarios)
        ).filter(
            Departamento.status == 1
        ).order_by(Departamento.nombre.asc()).all() # <--- CAMBIO: Ordenar Alfabéticamente (A-Z)
        
        return depts
    except Exception as e:
        print(f"Error al obtener departamentos: {e}")
        return []
    finally:
        db.close()

# ==========================================
# ESCRITURA (CREATE / UPDATE)
# ==========================================

def create_department(nombre: str, code: int):
    db: Session = next(get_db())
    try:
        nombre_limpio = nombre.strip()
        
        # 1. Validar Nombre Duplicado
        existing_name = db.query(Departamento).filter(func.lower(Departamento.nombre) == nombre_limpio.lower()).first()
        if existing_name:
            if existing_name.status == 0:
                # Opcional: Podríamos reactivar, pero cuidando el código.
                # Simplificación: No permitimos reactivar si el código choca con otro activo.
                return {"status": "error", "message": "El nombre del departamento ya existe (inactivo o activo)."}
            return {"status": "error", "message": "El nombre del departamento ya existe."}

        # 2. Validar Código Duplicado
        existing_code = db.query(Departamento).filter(Departamento.code == code).first()
        if existing_code:
            return {"status": "error", "message": "El código del departamento ya existe."}

        new_dept = Departamento(nombre=nombre_limpio, code=code, status=1)
        db.add(new_dept)
        db.commit()
        
        return {"status": "success", "message": "Departamento creado correctamente."} 
        
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"Error en BD: {str(e)}"}
    finally:
        db.close()

def update_department(dept_id: int, nombre: str, code: int):
    db: Session = next(get_db())
    try:
        nombre_limpio = nombre.strip()
        
        dept = db.query(Departamento).filter(Departamento.id == dept_id).first()
        if not dept: return {"status": "error", "message": "No encontrado"}
        
        # 1. Validar Nombre Duplicado (Excluyendo actual)
        existing_name = db.query(Departamento).filter(
            func.lower(Departamento.nombre) == nombre_limpio.lower(), 
            Departamento.id != dept_id
        ).first()
        if existing_name: return {"status": "error", "message": "El nombre ya existe"}

        # 2. Validar Código Duplicado (Excluyendo actual)
        existing_code = db.query(Departamento).filter(
            Departamento.code == code, 
            Departamento.id != dept_id
        ).first()
        if existing_code: return {"status": "error", "message": "El código ya existe"}

        dept.nombre = nombre_limpio
        dept.code = code
        db.commit()
        
        return {"status": "success", "message": "Departamento modificado correctamente."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def delete_department_logical(dept_id: int):
    db: Session = next(get_db())
    try:
        dept = db.query(Departamento).filter(Departamento.id == dept_id).first()
        if not dept: return {"status": "error", "message": "No encontrado"}
        
        dept.status = 0
        db.commit()
        
        # MENSAJE DE ÉXITO CLARO
        return {"status": "success", "message": "Departamento eliminado correctamente."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def delete_department_physical(dept_id: int):
    """Baja Física: Elimina la fila de la BD. Cuidado con integridad referencial."""
    db: Session = next(get_db())
    try:
        dept = db.query(Departamento).filter(Departamento.id == dept_id).first()
        if not dept:
            return {"status": "error", "message": "Departamento no encontrado."}
        
        db.delete(dept)
        db.commit()
        return {"status": "success", "message": "Departamento eliminado permanentemente."}
    
    except IntegrityError:
        db.rollback()
        # Esto pasa si intentas borrar un depto que tiene usuarios asignados
        return {
            "status": "error", 
            "message": "No se puede eliminar: Hay usuarios o datos asociados a este departamento."
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()