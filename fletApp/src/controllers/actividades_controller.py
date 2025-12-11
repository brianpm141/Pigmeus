import bcrypt
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from db.database import get_db
from db.models import Actividad, Usuario, Categoria, Departamento, Proyecto, Colaborador

# ==========================================
# LECTURA (READ)
# ==========================================

def get_activities(current_user=None, filter_dept_id=None):
    db: Session = next(get_db())
    try:
        query = db.query(Actividad).options(
            joinedload(Actividad.usuario_rel).joinedload(Usuario.departamento),
            joinedload(Actividad.categoria_rel).joinedload(Categoria.departamento_rel),
            joinedload(Actividad.proyecto_rel),
            joinedload(Actividad.colaboradores).joinedload(Colaborador.usuario_rel) # <--- Cargar colaboradores
        ).filter(Actividad.status == 1)
        
        # Filtrado por Rol / Contexto
        if current_user:
             # Caso A: Es un objeto Usuario
             if hasattr(current_user, 'role'):
                 role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
                 
                 # Si ES Admin y hay filtro explicito -> aplicarlo
                 if "Administrador" in role_str:
                     if filter_dept_id and filter_dept_id != "all":
                         query = query.join(Usuario, Actividad.usuario_rel).filter(Usuario.departamento_id == filter_dept_id)
                 
                 # Si ES Gerente -> Ver todo su departamento
                 elif "Gerente" in role_str:
                     query = query.join(Usuario, Actividad.usuario_rel).filter(Usuario.departamento_id == current_user.departamento_id)

                 # Si ES Básico -> Ver SOLO sus actividades
                 else:
                     query = query.filter(Actividad.usuario_id == current_user.id)
             
             # Caso B: Es un objeto Departamento (Login Invitado)
             elif hasattr(current_user, 'code') and not hasattr(current_user, 'role'):
                 dept_id = current_user.id
                 query = query.join(Usuario, Actividad.usuario_rel).filter(Usuario.departamento_id == dept_id)

        activities = query.order_by(Actividad.created_at.desc()).all()
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
