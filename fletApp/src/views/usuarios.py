import flet as ft
import views.styles as styles
import controllers.usuarios_controller as controller 
from views.pops.usuario import UserForm
from views.pops.eliminar import ConfirmationDialog
from views.pops.mensaje import Aviso

class UsersView(ft.Container):
    def __init__(self, current_user):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.current_user = current_user
        
        # Inicializar componentes
        self._init_layout_components()

        self.content = ft.Column(
            controls=[
                self.header,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.toolbar,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.data_container
            ],
        )
        
        self.data_container.expand = True
        
        # Estado: ID del usuario seleccionado
        self.selected_id = None 
        
        # Cargar datos iniciales
        self.refresh_data()

    # --- MANEJADORES DE EVENTOS ---

    def _handle_select(self, e):
        """Lógica de selección única"""
        is_selected = e.data == "true"
        user_id = e.control.data 
        
        if is_selected:
            self.selected_id = user_id
        else:
            if self.selected_id == user_id:
                self.selected_id = None
        
        self.refresh_data()

    def _open_create_modal(self, e):
        form = UserForm(e.page, on_success=self.refresh_data, current_user=self.current_user)
        form.show()

    def _open_modify_modal(self, e):
        if not self.selected_id:
            self._show_aviso("Selecciona un usuario para modificar", is_error=True)
            return
        
        # Pasamos current_user al controller también si hiciera falta lógica extra, pero aquí recuperamos 1
        # Sin embargo, get_all_users ya filtra, así que si intentan modificar uno que no ven, fallaría (bien).
        all_users = controller.get_all_users(self.current_user)
        selected_user = next((u for u in all_users if u.id == self.selected_id), None)

        if selected_user:
            # Crear diccionario compatible con el formulario
            # Aseguramos obtener el valor string del Enum
            role_val = selected_user.role.value if hasattr(selected_user.role, 'value') else selected_user.role
            
            # --- Validacion Extra: Gerente no puede editar Admin ---
            if self.current_user:
                my_role = str(self.current_user.role.value) if hasattr(self.current_user.role, 'value') else str(self.current_user.role)
                target_role = str(role_val)
                
                # Si soy Gerente (y no Admin) y quiero editar a un Admin -> Error
                if "Gerente" in my_role and "Administrador" not in my_role:
                    if "Administrador" in target_role:
                        self._show_aviso("No tienes permisos para modificar a un Administrador.", is_error=True)
                        return
            
            user_dict = {
                "id": selected_user.id,
                "user": selected_user.username, # Username
                "nombre": selected_user.nombre,
                "apellidos": selected_user.apellidos,
                "matricula": selected_user.matricula, # Si usaste matricula en el modelo
                "departamento_id": selected_user.departamento_id,
                "role": role_val
            }
            
            form = UserForm(e.page, user_data=user_dict, on_success=self.refresh_data, current_user=self.current_user)
            form.show()

    def _delete_handler(self, e):
        if not self.selected_id:
            self._show_aviso("Selecciona un usuario para eliminar", is_error=True)
            return

        dialog = ConfirmationDialog(
            self.page,
            title="Eliminar Usuario",
            content_text="¿Estás seguro de que deseas dar de baja a este usuario?",
            on_confirm=self._execute_delete
        )
        dialog.show()

    def _execute_delete(self):
        result = controller.delete_user_logical(self.selected_id)
        
        if result["status"] == "success":
            self.selected_id = None
            self.refresh_data()
            self._show_aviso(result["message"], is_error=False)
        else:
            self._show_aviso(result["message"], is_error=True)

    def _show_aviso(self, msg, is_error=False):
        """Helper rápido para mostrar avisos simples"""
        aviso = Aviso(self.page, message=msg, is_error=is_error)
        aviso.show()

    # --- UI LAYOUT ---

    def _init_layout_components(self):
        # Header
        self.header = ft.Text("Usuarios", size=24, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR)

        self.toolbar = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Crear Usuario",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    bgcolor=styles.BTN_PRIMARY_BG,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(vertical=20)
                    ),
                    on_click=self._open_create_modal,
                    expand=1
                ),
                ft.ElevatedButton(
                    "Modificar Usuario",
                    icon=ft.Icons.EDIT_OUTLINED,
                    bgcolor=styles.BTN_MODIFY_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(vertical=20)
                    ),
                    on_click=self._open_modify_modal,
                    expand=1
                ),
                ft.ElevatedButton(
                    "Eliminar Usuario",
                    icon=ft.Icons.DELETE_OUTLINE,
                    bgcolor=styles.BTN_DELETE_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(vertical=20)
                    ),
                    on_click=self._delete_handler,
                    expand=1
                ),
                ft.Container(expand=1)
            ],
            spacing=15
        )

        self.data_container = ft.Container()

    def _build_card(self, user):
        is_selected = (user.id == self.selected_id)
        
        nombre_completo = f"{user.nombre} {user.apellidos}"
        depto_nombre = user.departamento.nombre if user.departamento else "Sin Asignar"
        role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)

        return ft.Container(
            content=ft.Row(
                controls=[
                    # Avatar/Icon Area
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREY_600),
                        padding=15,
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=10,
                    ),
                    # Info Area
                    ft.Column(
                        controls=[
                            ft.Text(nombre_completo, weight=ft.FontWeight.BOLD, size=16, color=styles.TEXT_COLOR),
                            ft.Text(f"{user.username} | {depto_nombre}", size=13, color=ft.Colors.GREY_500),
                            ft.Container(
                                content=ft.Text(role_str.upper(), size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=styles.PRIMARY_BLUE,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_radius=10
                            )
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                ],
                spacing=20,
            ),
            padding=ft.padding.all(15),
            bgcolor=styles.CARD_BG,
            border_radius=12,
            shadow=styles.CARD_SHADOW if not is_selected else None,
            border=ft.border.all(2, styles.PRIMARY_BLUE) if is_selected else None,
            on_click=lambda e: self._on_card_click(user.id),
            ink=True
        )

    def _on_card_click(self, user_id):
        if self.selected_id == user_id:
            self.selected_id = None
        else:
            self.selected_id = user_id
        self.refresh_data()

    def refresh_data(self):
        users_data = controller.get_all_users(self.current_user)

        if users_data and len(users_data) > 0:
            cards = []
            for user in users_data:
                cards.append(self._build_card(user))

            self.data_container.alignment = ft.alignment.top_center
            self.data_container.content = ft.ListView(
                controls=cards,
                spacing=15,
                padding=ft.padding.only(bottom=20)
            )
        else:
            # Empty State
            self.data_container.alignment = ft.alignment.center
            self.data_container.content = ft.Column(
                controls=[
                    ft.Icon(name=ft.Icons.PERSON_OFF_OUTLINED, size=60, color=ft.Colors.GREY_300),
                    ft.Text("No hay usuarios registrados.", color=ft.Colors.GREY_500, size=16)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
        
        if self.data_container.page:
            self.data_container.update()