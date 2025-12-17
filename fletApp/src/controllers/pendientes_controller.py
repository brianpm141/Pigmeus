from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from db.database import get_db
from db.models import Pendiente, Usuario, Categoria

# ==========================================
# LECTURA (READ)
# ==========================================

def get_pendientes(
    current_user=None, 
    filter_category_id=None, 
    filter_status_int=None, 
    filter_date_start=None,
    filter_date_end=None,
    sort_by="created_at", 
    sort_desc=True
):
    db: Session = next(get_db())
    try:
        query = db.query(Pendiente).options(
            joinedload(Pendiente.usuario_rel),
            joinedload(Pendiente.categoria_rel).joinedload(Categoria.departamento_rel)
        ).filter(Pendiente.status == 1)
        
        # --- 1. Filtrado de Seguridad (Siempre personales por ahora) ---
        if current_user:
             # Si se quiere permitir a admin ver todo, se añadiría lógica aquí.
             # Por ahora, estricto a personales como dice la descripción.
             if hasattr(current_user, 'id'):
                 query = query.filter(Pendiente.usuario_id == current_user.id)

        # --- 2. Filtros Específicos ---
        if filter_category_id and str(filter_category_id) != "all":
            query = query.filter(Pendiente.categoria_id == int(filter_category_id))
            
        if filter_status_int is not None and str(filter_status_int) != "all":
            query = query.filter(Pendiente.estado == int(filter_status_int))
        
        # --- 3. Ordenamiento ---
        sort_column = Pendiente.created_at # Default
        if sort_by == "fecha_asignada":
            sort_column = Pendiente.fecha_asignada
        elif sort_by == "fecha_completada":
            sort_column = Pendiente.fecha_completada
        
        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        pendientes = query.all()
        return pendientes
    except Exception as e:
        print(f"Error al obtener pendientes: {e}")
        return []
    finally:
        db.close()

# ==========================================
# ESCRITURA (CREATE)
# ==========================================

def create_pendiente(user_id: int, category_id: int, description: str, fecha_asignada: datetime = None, status_str: str = "Pendiente"):
    db: Session = next(get_db())
    try:
        # Estado
        estado_int = 1 if status_str == "Completada" else 0
        fecha_completada = datetime.now() if estado_int == 1 else None

        new_pendiente = Pendiente(
            descripcion=description,
            fecha_asignada=fecha_asignada,
            fecha_completada=fecha_completada,
            estado=estado_int,
            categoria_id=category_id,
            usuario_id=user_id,
            status=1
        )
        
        db.add(new_pendiente)
        db.commit()
        return {"status": "success", "message": "Pendiente registrado correctamente."}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"Error en BD: {str(e)}"}
    finally:
        db.close()

# ==========================================
# ACTUALIZACIÓN (UPDATE)
# ==========================================

def update_pendiente_status(pendiente_id: int, new_status_str: str):
    db: Session = next(get_db())
    try:
        pendiente = db.query(Pendiente).filter(Pendiente.id == pendiente_id).first()
        if not pendiente:
            return {"status": "error", "message": "Pendiente no encontrado."}

        estado_int = 1 if new_status_str == "Completada" else 0
        
        if estado_int == 1 and pendiente.estado != 1:
            pendiente.fecha_completada = datetime.now()
        elif estado_int == 0:
            pendiente.fecha_completada = None

        pendiente.estado = estado_int
        db.commit()
        return {"status": "success", "message": "Estado actualizado."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def update_pendiente(pendiente_id: int, category_id: int, description: str, fecha_asignada: datetime, status_str: str):
    db: Session = next(get_db())
    try:
        pendiente = db.query(Pendiente).filter(Pendiente.id == pendiente_id).first()
        if not pendiente:
            return {"status": "error", "message": "Pendiente no encontrado."}

        estado_int = 1 if status_str == "Completada" else 0
        
        # Fecha completada logic
        if estado_int == 1 and pendiente.estado != 1:
            pendiente.fecha_completada = datetime.now()
        elif estado_int == 0:
            pendiente.fecha_completada = None

        pendiente.categoria_id = category_id
        pendiente.descripcion = description
        pendiente.fecha_asignada = fecha_asignada
        pendiente.estado = estado_int
        
        db.commit()
        return {"status": "success", "message": "Pendiente actualizado."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# ==========================================
# ELIMINACIÓN (DELETE)
# ==========================================

def delete_pendiente(pendiente_id: int):
    db: Session = next(get_db())
    try:
        pendiente = db.query(Pendiente).filter(Pendiente.id == pendiente_id).first()
        if not pendiente:
            return {"status": "error", "message": "Pendiente no encontrado."}
        
        pendiente.status = 0 # Soft delete
        db.commit()
        return {"status": "success", "message": "Pendiente eliminado."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
