from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from db.database import get_db_context
from db.models import Actividad, Categoria, Usuario
from datetime import datetime

# ==========================================
# LECTURA (READ)
# ==========================================

def get_all_activities():
    with get_db_context() as db:
        try:
            activities = db.query(Actividad).options(
                joinedload(Actividad.usuario_rel),
                joinedload(Actividad.categoria_rel)
            ).filter(
                Actividad.status == 1
            ).order_by(Actividad.created_at.desc()).all()
            
            return activities
        except Exception as e:
            print(f"Error al obtener actividades: {e}")
            return []

def get_categories():
    with get_db_context() as db:
        try:
            # Asumimos que queremos todas las categorías activas
            # Podríamos filtrar por departamento si fuera necesario, pero por ahora todas.
            categories = db.query(Categoria).filter(Categoria.status == 1).order_by(Categoria.nombre.asc()).all()
            return categories
        except Exception as e:
            print(f"Error al obtener categorías: {e}")
            return []

# ==========================================
# ESCRITURA (CREATE / UPDATE)
# ==========================================

def create_activity(descripcion: str, categoria_id: int, dept_id: int, user_id: int, prioridad: int = 1, estado: int = 0):
    with get_db_context() as db:
        try:
            # Lógica solicitada:
            # - Tipo siempre 0 (Genérica)
            # - Hora inicio = Ahora
            
            tipo = 0
            horainicio = datetime.now()
            
            # Si se crea ya completada, la hora de cierre es la misma que la de inicio
            horacierre = horainicio if estado == 1 else None
            
            new_activity = Actividad(
                descripcion=descripcion,
                horainicio=horainicio,
                horacierre=horacierre,
                estado=estado,
                tipo=tipo,
                prioridad=prioridad,
                usuario_id=user_id,
                categoria_id=categoria_id,
                departamento_id=dept_id,
                proyecto_id=None, # Tipo 0 no lleva proyecto
                status=1
            )
            
            db.add(new_activity)
            db.commit()
            
            return {"status": "success", "message": "Actividad registrada correctamente."}
            
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": f"Error en BD: {str(e)}"}

def update_activity(activity_id: int, descripcion: str, categoria_id: int, estado: int, prioridad: int = 1):
    with get_db_context() as db:
        try:
            activity = db.query(Actividad).filter(Actividad.id == activity_id).first()
            if not activity: return {"status": "error", "message": "Actividad no encontrada"}
            
            # Actualizamos datos básicos
            activity.descripcion = descripcion
            activity.categoria_id = categoria_id
            activity.prioridad = prioridad
            
            # Lógica de Fechas según Estado
            # Si cambia A COMPLETADO (1) y antes no lo estaba -> Ponemos fecha cierre
            if estado == 1 and activity.estado != 1:
                activity.horacierre = datetime.now()
                
            # Si cambia A PENDIENTE (0) y antes estaba completo -> Borramos fecha cierre
            elif estado == 0 and activity.estado == 1:
                activity.horacierre = None
                
            activity.estado = estado
            
            db.commit()
            return {"status": "success", "message": "Actividad modificada correctamente."}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}

def delete_activity_logical(activity_id: int):
    with get_db_context() as db:
        try:
            activity = db.query(Actividad).filter(Actividad.id == activity_id).first()
            if not activity: return {"status": "error", "message": "No encontrada"}
            
            activity.status = 0
            db.commit()
            
            return {"status": "success", "message": "Actividad eliminada correctamente."}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
