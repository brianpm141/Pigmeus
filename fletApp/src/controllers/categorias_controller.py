
from db.models import Categoria, Departamento
from sqlalchemy import func
from sqlalchemy.orm import joinedload

# ==========================================
# LECTURA (READ)
# ==========================================

def get_all_categories(current_user=None):
    # IMPORTACIÓN LOCAL (Mueve el import aquí dentro)
    from db.database import get_db_context 
    
    with get_db_context() as db:
        try:
            query = db.query(Categoria).options(
                joinedload(Categoria.departamento_rel)
            ).filter(Categoria.status == 1)
            
            # Filtrado por Rol / Contexto
            if current_user:
                 # Caso A: Usuario
                 if hasattr(current_user, 'role'):
                     role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
                     
                     if "Administrador" not in role_str:
                         query = query.filter(Categoria.departamento_id == current_user.departamento_id)
                
                 # Caso B: Departamento (Invitado)
                 elif hasattr(current_user, 'code'):
                     query = query.filter(Categoria.departamento_id == current_user.id)
            else:
                 # print("DEBUG: current_user is None in get_all_categories")
                 # FAIL CLOSED: Si no hay usuario, no mostramos nada (seguridad)
                 return []

            categories = query.order_by(Categoria.nombre.asc()).all()
            
            return categories
        except Exception as e:
            print(f"Error al obtener categorías: {e}")
            return []

# ==========================================
# ESCRITURA (CREATE / UPDATE)
# ==========================================

def create_category(nombre: str, dept_id: int):
    # IMPORTACIÓN LOCAL
    from db.database import get_db_context 

    with get_db_context() as db:
        try:
            nombre_limpio = nombre.strip()
            # Validar duplicado en el mismo departamento
            existing = db.query(Categoria).filter(
                func.lower(Categoria.nombre) == nombre_limpio.lower(),
                Categoria.departamento_id == dept_id
            ).first()

            if existing:
                if existing.status == 0:
                    existing.status = 1
                    existing.nombre = nombre_limpio
                    db.commit()
                    return {"status": "success", "message": "Categoría reactivada exitosamente."}
                else:
                    return {"status": "error", "message": "Ya existe una categoría con ese nombre en el departamento."}

            new_cat = Categoria(
                nombre=nombre_limpio,
                departamento_id=dept_id,
                status=1
            )
            db.add(new_cat)
            db.commit()
            
            return {"status": "success", "message": "Categoría creada correctamente."}
            
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": f"Error en BD: {str(e)}"}

def update_category(cat_id: int, nombre: str, dept_id: int):
    # IMPORTACIÓN LOCAL
    from db.database import get_db_context 

    with get_db_context() as db:
        # ... (resto de tu código igual) ...
        try:
            cat = db.query(Categoria).filter(Categoria.id == cat_id).first()
            if not cat: return {"status": "error", "message": "Categoría no encontrada"}
            
            nombre_limpio = nombre.strip()
            
            existing = db.query(Categoria).filter(
                func.lower(Categoria.nombre) == nombre_limpio.lower(),
                Categoria.departamento_id == dept_id,
                Categoria.id != cat_id
            ).first()
            
            if existing: return {"status": "error", "message": "El nombre ya existe en este departamento"}

            cat.nombre = nombre_limpio
            cat.departamento_id = dept_id
            
            db.commit()
            return {"status": "success", "message": "Categoría modificada correctamente."}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}

def delete_category_logical(cat_id: int):
    # IMPORTACIÓN LOCAL
    from db.database import get_db_context 

    with get_db_context() as db:
        try:
            cat = db.query(Categoria).filter(Categoria.id == cat_id).first()
            if not cat: return {"status": "error", "message": "No encontrada"}
            
            cat.status = 0
            db.commit()
            
            return {"status": "success", "message": "Categoría eliminada correctamente."}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}