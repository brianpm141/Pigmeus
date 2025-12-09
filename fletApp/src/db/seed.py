import bcrypt
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Departamento, Categoria, Usuario, Password, UserRole, Actividad

def seed_data():
    db: Session = next(get_db())
    try:
        # Verificar si ya existen departamentos
        if db.query(Departamento).first():
            print("La base de datos ya contiene datos. Saltando seed.")
            return

        print("Inicializando datos de prueba (Seed Robusto)...")

        # Configuración
        dept_names = ["Recursos Humanos", "Desarrollo", "Ventas"]
        cat_names_base = ["Soporte", "Gestión", "Reunión", "Documentación", "Desarrollo"]
        
        # Helper para hash
        def hash_pass(raw):
            return bcrypt.hashpw(raw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user_count_global = 1

        # 1. Crear Departamentos
        for d_idx, d_name in enumerate(dept_names):
            print(f" -> Creando Departamento: {d_name}")
            dept = Departamento(
                nombre=d_name, 
                code=1234, # 1000, 1001, 1002
                status=1
            )
            db.add(dept)
            db.flush() # ID necesario

            # 2. Crear 3 Categorías por Departamento
            cats_objs = []
            selected_cat_names = random.sample(cat_names_base, 3) # 3 nombres random o fijos
            # Para ser mas deterministas, usaremos fijos + indice si se prefiere, pero random esta bien
            # Mejor fijos para que tenga sentido
            cat_fixed = [f"General {d_name}", f"Proyectos {d_name}", f"Urgencias {d_name}"]
            
            for c_name in cat_fixed:
                cat = Categoria(nombre=c_name, departamento_id=dept.id, status=1)
                db.add(cat)
                db.flush()
                cats_objs.append(cat)
            
            # 3. Crear 3 Usuarios por Departamento
            # Roles: 1 Gerente, 2 Básicos (por ejemplo)
            roles_dist = [UserRole.GERENTE, UserRole.BASICO, UserRole.BASICO]
            
            for u_idx in range(3):
                role = roles_dist[u_idx]
                username = f"user_{d_name[:3].lower()}_{u_idx+1}" # user_rec_1
                if role == UserRole.GERENTE:
                    username = f"gerente_{d_name[:3].lower()}" # gerente_rec

                # Crear Password
                p_obj = Password(hash=hash_pass("1234"))
                db.add(p_obj)
                db.flush()

                user = Usuario(
                    username=username,
                    pass_id=p_obj.id,
                    nombre=f"Usuario{u_idx+1}",
                    apellidos=f"De {d_name}",
                    matricula=f"EMP{user_count_global:03d}",
                    role=role,
                    departamento_id=dept.id,
                    status=1
                )
                db.add(user)
                db.flush()
                user_count_global += 1

                # 4. Crear 10 Actividades por Usuario (Diferentes)
                for a_idx in range(10):
                    # Randomizar datos
                    cat = random.choice(cats_objs)
                    state_int = random.choice([0, 1]) # 0 Pendiente, 1 Completada
                    
                    # Fechas
                    days_ago = random.randint(0, 30)
                    start_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(1, 8))
                    end_time = None
                    if state_int == 1:
                        end_time = start_time + timedelta(hours=random.randint(1, 4))
                    
                    act = Actividad(
                        descripcion=f"Actividad {a_idx+1} de {user.username} - {cat.nombre}",
                        horainicio=start_time,
                        horacierre=end_time,
                        estado=state_int,
                        tipo=1,
                        usuario_id=user.id,
                        categoria_id=cat.id,
                        proyecto_id=None, # Opcional
                        status=1
                    )
                    db.add(act)
        
        # Crear Admin Global (Extra, fuera de los 3 deptos o en uno de ellos? El prompt dice 3 deptos, pondré admin en el primero pero manual o aparte)
        # Para cumplir estrictamente "3 usuarios por departamento", el admin podría ser uno de esos o uno extra.
        # Crearé un usuario "admin" extra en el primer depto para no perder acceso admin
        first_dept = db.query(Departamento).first()
        if first_dept:
             p_admin = Password(hash=hash_pass("admin123"))
             db.add(p_admin)
             db.flush()
             admin_user = Usuario(
                username="admin",
                pass_id=p_admin.id,
                nombre="Super",
                apellidos="Admin",
                matricula="ADM001",
                role=UserRole.ADMIN,
                departamento_id=first_dept.id,
                status=1
             )
             db.add(admin_user)

        print(" -> Usuarios y Actividades creados.")
        
        db.commit()
        print("Seed completado exitosamente.")

    except Exception as e:
        db.rollback()
        print(f"Error durante seeding: {e}")
    finally:
        db.close()
