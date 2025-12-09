from sqlalchemy.orm import Session, joinedload
from db.database import get_db
from db.models import Proyecto, Usuario, Departamento
from datetime import datetime

def get_projects(current_user=None, filter_dept_id=None):
    db: Session = next(get_db())
    try:
        query = db.query(Proyecto).options(
            joinedload(Proyecto.responsable_rel),
            joinedload(Proyecto.departamento_rel)
        ).filter(Proyecto.status == 1)
        
        # RBAC Filtering
        if current_user:
            # Case A: Usuario Object
            if hasattr(current_user, 'role'):
                role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
                if "Administrador" in role_str:
                     if filter_dept_id and filter_dept_id != "all":
                         query = query.filter(Proyecto.departamento_id == filter_dept_id)
                else:
                     query = query.filter(Proyecto.departamento_id == current_user.departamento_id)
            
            # Case B: Departamento Object (Guest)
            elif hasattr(current_user, 'code'):
                query = query.filter(Proyecto.departamento_id == current_user.id)
        
        return query.order_by(Proyecto.created_at.desc()).all()
    except Exception as e:
        print(f"Error getting projects: {e}")
        return []
    finally:
        db.close()

def create_project(nombre, responsable_id, departamento_id, fecha_est=None):
    db: Session = next(get_db())
    try:
        new_proj = Proyecto(
            nombre=nombre,
            responsable_id=responsable_id,
            departamento_id=departamento_id,
            fecha_est=fecha_est,
            status=1
        )
        db.add(new_proj)
        db.commit()
        return {"status": "success", "message": "Proyecto creado correctamente."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def update_project(proj_id, nombre, responsable_id, departamento_id, fecha_est=None):
    db: Session = next(get_db())
    try:
        proj = db.query(Proyecto).filter(Proyecto.id == proj_id).first()
        if not proj:
            return {"status": "error", "message": "Proyecto no encontrado."}
            
        proj.nombre = nombre
        proj.responsable_id = responsable_id
        proj.departamento_id = departamento_id
        proj.fecha_est = fecha_est
        proj.fecha_mov = datetime.now()
        
        db.commit()
        return {"status": "success", "message": "Proyecto actualizado."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def delete_project(proj_id):
    db: Session = next(get_db())
    try:
        proj = db.query(Proyecto).filter(Proyecto.id == proj_id).first()
        if not proj:
            return {"status": "error", "message": "No encontrado."}
        
        proj.status = 0
        db.commit()
        return {"status": "success", "message": "Proyecto eliminado."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
