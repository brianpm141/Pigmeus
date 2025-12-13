import bcrypt
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from db.database import get_db
from db.models import Actividad, Usuario, Categoria, Departamento, Proyecto, Colaborador

# ==========================================
# LECTURA (READ)
# ==========================================

from sqlalchemy import or_

# ...

from datetime import datetime, timedelta
from sqlalchemy import or_, case, func

# ...

def get_activities(
    current_user=None, 
    filter_dept_id=None, 
    filter_user_id=None, 
    filter_category_id=None, 
    filter_status_int=None, 
    filter_date_start=None,
    filter_date_end=None,
    sort_by="created_at", 
    sort_desc=True
):
    db: Session = next(get_db())
    try:
        query = db.query(Actividad).options(
            joinedload(Actividad.usuario_rel).joinedload(Usuario.departamento),
            joinedload(Actividad.categoria_rel).joinedload(Categoria.departamento_rel),
            joinedload(Actividad.proyecto_rel),
            joinedload(Actividad.colaboradores).joinedload(Colaborador.usuario_rel)
        ).filter(Actividad.status == 1)
        
        # ... (Context Filters - same as before) ...
        # --- 1. Filtrado de Seguridad (Contexto) ---
        if current_user:
             if hasattr(current_user, 'role'):
                 role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
                 
                 if "Administrador" in role_str:
                     if filter_dept_id and filter_dept_id != "all":
                         query = query.join(Usuario, Actividad.usuario_rel).filter(Usuario.departamento_id == filter_dept_id)
                 
                 elif "Gerente" in role_str:
                     query = query.join(Usuario, Actividad.usuario_rel).filter(Usuario.departamento_id == current_user.departamento_id)

                 else:
                     query = query.filter(Actividad.usuario_id == current_user.id)
             
             elif hasattr(current_user, 'code'):
                 dept_id = current_user.id
                 query = query.join(Usuario, Actividad.usuario_rel).filter(Usuario.departamento_id == dept_id)

        # --- 2. Filtros Específicos (Columnas) ---
        if filter_user_id and str(filter_user_id) != "all":
            f_uid = int(filter_user_id)
            query = query.filter(
                or_(
                    Actividad.usuario_id == f_uid,
                    Actividad.colaboradores.any(Colaborador.usuario_id == f_uid)
                )
            )
            
        if filter_category_id and str(filter_category_id) != "all":
            query = query.filter(Actividad.categoria_id == filter_category_id)
            
        if filter_status_int is not None and str(filter_status_int) != "all":
            query = query.filter(Actividad.estado == int(filter_status_int))
        
        # --- Filtros de Fecha ---
        now = datetime.now()
        
        def get_cutoff(period):
            if period == "1h": return now - timedelta(hours=1)
            if period == "today": return now.replace(hour=0, minute=0, second=0, microsecond=0)
            if period == "week": 
                # Start of week (Monday)
                start_week = now - timedelta(days=now.weekday())
                return start_week.replace(hour=0, minute=0, second=0, microsecond=0)
            if period == "month": return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return None

        # Fecha Inicio
        if filter_date_start and filter_date_start != "all":
            cutoff = get_cutoff(filter_date_start)
            if cutoff:
                query = query.filter(Actividad.horainicio >= cutoff)
        
        # Fecha Fin (Si horacierre es NULL -> Usar NOW)
        if filter_date_end and filter_date_end != "all":
            cutoff = get_cutoff(filter_date_end)
            if cutoff:
                # Lógica: COALESCE(horacierre, NOW()) >= cutoff
                # case when horacierre is null then now else horacierre end
                # SQLAlchemy: func.coalesce(Actividad.horacierre, now) 
                # Note: 'now' python var is fixed at function start. Ideally use DB sysdate but python 'now' is close enough.
                query = query.filter(func.coalesce(Actividad.horacierre, now) >= cutoff)

        # --- 3. Ordenamiento ---
        sort_column = Actividad.created_at # Default
        if sort_by == "horainicio":
            sort_column = Actividad.horainicio
        elif sort_by == "horacierre":
            # Sort treating NULL as NOW? User didn't specify sort logic for nulls, but logical consistency suggests yes.
            # However, standard sort is fine.
            sort_column = Actividad.horacierre
        
        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        activities = query.all()
        return activities
    except Exception as e:
        print(f"Error al obtener actividades: {e}")
        return []
    finally:
        db.close()

# ==========================================
# ESCRITURA (CREATE)
# ==========================================

def create_activity(user_id: int, password_attempt: str, category_id: int, details: str, status_str: str, collaborator_ids: list = None, skip_password_check=False):
    db: Session = next(get_db())
    try:
        # 1. Validar Usuario y Contraseña
        user = db.query(Usuario).options(joinedload(Usuario.password)).filter(Usuario.id == user_id).first()
        if not user:
            return {"status": "error", "message": "Usuario no encontrado."}
        
        # Verificar password (si no se salta)
        if not skip_password_check:
            if not bcrypt.checkpw(password_attempt.encode('utf-8'), user.password.hash.encode('utf-8')):
                return {"status": "error", "message": "Contraseña incorrecta."}

        # 2. Configurar Fechas y Estado
        now = datetime.now()
        horainicio = now
        horacierre = None
        
        # Mapear estado string a int (según convención, asumo 0=Pendiente, 1=Completada por ahora, o usar el string si el modelo lo permite, pero el modelo dice Integer)
        # Revisando models.py: estado = Column(Integer, default=0)
        # Asumiremos: 0 = Pendiente, 1 = Completada
        estado_int = 1 if status_str == "Completada" else 0
        
        if estado_int == 1:
            horacierre = now

        # 3. Datos adicionales (Proyecto)
        # Proyecto? models.py permite null. Lo dejamos null por ahora si no se pide.
        proyecto_id = None

        # 4. Crear Actividad
        new_activity = Actividad(
            descripcion=details,
            horainicio=horainicio,
            horacierre=horacierre,
            estado=estado_int,
            tipo=1, # Tipo dummy por ahora, models requiere int
            usuario_id=user.id,
            categoria_id=category_id,
            proyecto_id=proyecto_id,
            status=1
        )
        
        db.add(new_activity)
        db.flush() # ID necesario para colaboradores
        
        # 5. Agregar Colaboradores
        if collaborator_ids:
            for c_id in collaborator_ids:
                # Evitar agregarse a sí mismo como colaborador? (Opcional, pero lógico)
                if c_id == user.id: continue
                
                new_collab = Colaborador(
                    actividad_id=new_activity.id,
                    usuario_id=c_id,
                    status=1
                )
                db.add(new_collab)

        db.commit()
        
        return {"status": "success", "message": "Actividad registrada correctamente."}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"Error en BD: {str(e)}"}
    finally:
        db.close()

# ==========================================
# ACTUALIZACIÓN (UPDATE)
# ==========================================

def update_activity_status(activity_id: int, new_status_str: str):
    db: Session = next(get_db())
    try:
        activity = db.query(Actividad).filter(Actividad.id == activity_id).first()
        if not activity:
            return {"status": "error", "message": "Actividad no encontrada."}

        estado_int = 1 if new_status_str == "Completada" else 0
        
        # Si cambia a completada y no tenía fecha de cierre, se la ponemos
        if estado_int == 1 and activity.estado != 1:
            activity.horacierre = datetime.now()
        
        # Si cambia a pendiente, quitamos la fecha de cierre? 
        # El prompt dice: "si se selecciona como completado se registra la misma hora... no se registra hora de cierre hasta que se modifique o se de marcar como completado"
        # Si vuelvo a pendiente, lógicamente debería borrar la fecha de cierre o dejarla?
        # "no se registra hora de cierre hasta que se modifique o se de marcar como completado"
        # Asumiré que si vuelve a pendiente, se limpia la fecha de cierre para ser consistente.
        if estado_int == 0:
            activity.horacierre = None

        activity.estado = estado_int
        db.commit()
        return {"status": "success", "message": "Estado actualizado."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def update_activity(activity_id: int, category_id: int, details: str, status_str: str, collaborator_ids: list = None):
    db: Session = next(get_db())
    try:
        activity = db.query(Actividad).filter(Actividad.id == activity_id).first()
        if not activity:
            return {"status": "error", "message": "Actividad no encontrada."}

        estado_int = 1 if status_str == "Completada" else 0
        
        # Actualizar cierre si cambia a completada
        if estado_int == 1 and activity.estado != 1:
            activity.horacierre = datetime.now()
        elif estado_int == 0:
            activity.horacierre = None

        activity.categoria_id = category_id
        activity.descripcion = details
        activity.estado = estado_int
        
        # Actualizar Colaboradores: Estrategia Delete All + Re-Insert
        # Borramos colaboradores previos de esta actividad
        db.query(Colaborador).filter(Colaborador.actividad_id == activity_id).delete()
        
        if collaborator_ids:
            for c_id in collaborator_ids:
                if c_id == activity.usuario_id: continue # No agregarse a sí mismo
                
                new_collab = Colaborador(
                    actividad_id=activity_id,
                    usuario_id=c_id, # DB model map: usuario_id -> 'usuario' column
                    status=1
                )
                db.add(new_collab)

        db.commit()
        return {"status": "success", "message": "Actividad actualizada."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# ==========================================
# ELIMINACIÓN (DELETE)
# ==========================================

def delete_activity(activity_id: int):
    db: Session = next(get_db())
    try:
        activity = db.query(Actividad).filter(Actividad.id == activity_id).first()
        if not activity:
            return {"status": "error", "message": "Actividad no encontrada."}
        
        activity.status = 0 # Borrado lógico
        db.commit()
        return {"status": "success", "message": "Actividad eliminada."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
