import sys
import os

# Set path to allow imports from src
sys.path.append(os.path.join(os.getcwd(), 'src'))

from db.database import SessionLocal, get_db
from db.models import Actividad, Colaborador, Usuario, Departamento
from controllers.usuarios_controller import get_all_users
from controllers.actividades_controller import create_activity, update_activity

def verify_logic():
    print("--- Verifying Collaborator Logic ---")
    session = SessionLocal()
    try:
        # 1. Fetch some data
        users = session.query(Usuario).all()
        if len(users) < 2:
            print("Not enough users to test collaboration (need at least 2).")
            return
        
        owner = users[0]
        collab_user = users[1]
        
        print(f"Owner: {owner.username}, Collab: {collab_user.username}")
        
        # 2. Test create_activity with collaborator
        print("Testing create_activity...")
        res = create_activity(
            user_id=owner.id,
            password_attempt="1234", # Assuming 1234 as in seed
            category_id=1,
            details="Actividad con colaborador TEST",
            status_str="Pendiente",
            collaborator_ids=[collab_user.id],
            skip_password_check=True # Skip password check for simplicity
        )
        print(f"Result: {res}")
        
        if res["status"] != "success":
            print("Failed to create activity")
            return

        # Verify DB
        last_act = session.query(Actividad).order_by(Actividad.id.desc()).first()
        collabs = session.query(Colaborador).filter(Colaborador.actividad == last_act.id).all()
        print(f"Activity ID: {last_act.id}, Colaboradores count: {len(collabs)}")
        
        if len(collabs) != 1 or collabs[0].usuario != collab_user.id:
            print("FAILED: Collaborator not saved correctly.")
        else:
            print("SUCCESS: Collaborator saved.")
            
        # 3. Test update_activity (Remove collaborator)
        print("Testing update_activity (remove collaborator)...")
        update_activity(
            activity_id=last_act.id,
            category_id=1,
            details="Updated details",
            status_str="Pendiente",
            collaborator_ids=[] # Empty list
        )
        
        collabs_after = session.query(Colaborador).filter(Colaborador.actividad == last_act.id).all()
        print(f"Colaboradores count after update: {len(collabs_after)}")
        
        if len(collabs_after) != 0:
             print("FAILED: Collaborator not removed.")
        else:
             print("SUCCESS: Collaborator removed.")

    except Exception as e:
        print(f"Exception during verification: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_logic()
