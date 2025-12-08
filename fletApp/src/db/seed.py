import bcrypt
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Departamento, Categoria, Usuario, Password, UserRole

def seed_data():
    db: Session = next(get_db())
    try:
        # Verificar si ya existen departamentos (Indicio de que la BD ya tiene datos)
        if db.query(Departamento).first():
            print("La base de datos ya contiene datos. Saltando seed.")
            return

        print("Inicializando datos de prueba (Seed)...")

        # 1. Departamentos
        # Lista de tuplas (Nombre, Codigo)
        depts_data = [
            ("Recursos Humanos", 1234), 
            ("Desarrollo", 1234), 
            ("Ventas", 1234), 
            ("Dirección", 1234),
            ("Producción", 1234)
        ]
        depts_objs = {}
        
        for name, code in depts_data:
            d = Departamento(nombre=name, code=code, status=1)
            db.add(d)
            db.flush() # Para obtener ID
            depts_objs[name] = d
        
        print(" -> Departamentos creados.")

        # 2. Categorías
        # Asignamos categorías comunes a todos los departamentos para simplificar
        cats_data = ["Categoria 1", "Categoria 2", "Categoria 3", "Categoria 4"]
        
        for d_name, d_obj in depts_objs.items():
            for c_name in cats_data:
                c = Categoria(nombre=c_name, departamento_id=d_obj.id, status=1)
                db.add(c)
        
        print(" -> Categorías creadas.")

        # 3. Usuarios
        # Función helper para hash
        def hash_pass(raw):
            return bcrypt.hashpw(raw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        users_to_create = [
            # (Username, Pass, Nombre, Apellido, Role, Dpto)
            ("admin", "admin123", "Administrador", "Sistema", UserRole.ADMIN, "Dirección"),
            ("gerente", "gerente123", "Gerente", "General", UserRole.GERENTE, "Dirección"),
            ("rh_user", "1234", "Ana", "López", UserRole.BASICO, "Recursos Humanos"),
            ("dev_user", "1234", "Carlos", "Dev", UserRole.BASICO, "Desarrollo"),
            ("sales_user", "1234", "Luis", "Ventas", UserRole.BASICO, "Ventas"),
        ]

        count = 1
        for user_data in users_to_create:
            username, pwd, nom, ape, role, d_name = user_data
            
            # Crear Password
            p_obj = Password(hash=hash_pass(pwd))
            db.add(p_obj)
            db.flush()

            # Crear Usuario
            u = Usuario(
                username=username,
                pass_id=p_obj.id,
                nombre=nom,
                apellidos=ape,
                matricula=f"EMP{count:03d}", # EMP001, EMP002...
                role=role,
                departamento_id=depts_objs[d_name].id,
                status=1
            )
            db.add(u)
            count += 1
        
        print(" -> Usuarios creados.")
        
        db.commit()
        print("Seed completado exitosamente.")

    except Exception as e:
        db.rollback()
        print(f"Error durante seeding: {e}")
    finally:
        db.close()
