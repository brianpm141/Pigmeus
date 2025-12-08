import flet as ft
import views.styles as styles
import controllers.usuarios_controller as controller 
from views.pops.usuario import UserForm
from views.pops.eliminar import ConfirmationDialog
from views.pops.mensaje import Aviso

class UsersView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        
        # Inicializar componentes
        self._init_layout_components()

        self.content = ft.Column(
            controls=[
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
        form = UserForm(e.page, on_success=self.refresh_data)
        form.show()

    def _open_modify_modal(self, e):
        if not self.selected_id:
            self._show_aviso("Selecciona un usuario para modificar", is_error=True)
            return

        # Obtener datos frescos de la BD
        all_users = controller.get_all_users()
        selected_user = next((u for u in all_users if u.id == self.selected_id), None)

        if selected_user:
            # Crear diccionario compatible con el formulario
            # Aseguramos obtener el valor string del Enum
            role_val = selected_user.role.value if hasattr(selected_user.role, 'value') else selected_user.role
            
            user_dict = {
                "id": selected_user.id,
                "user": selected_user.username, # Username
                "nombre": selected_user.nombre,
                "apellidos": selected_user.apellidos,
                "matricula": selected_user.matricula, # Si usaste matricula en el modelo
                "departamento_id": selected_user.departamento_id,
                "role": role_val
            }
            
            form = UserForm(e.page, user_data=user_dict, on_success=self.refresh_data)
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
        self.toolbar = ft.Row(
            wrap=True,
            spacing=15,
            controls=[
                ft.ElevatedButton(
                    "Crear Usuario",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    bgcolor=styles.BTN_PRIMARY_BG,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=20, vertical=12)
                    ),
                    on_click=self._open_create_modal,
                    height=45
                ),
                ft.ElevatedButton(
                    "Modificar Usuario",
                    icon=ft.Icons.EDIT_OUTLINED,
                    bgcolor=styles.BTN_MODIFY_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=self._open_modify_modal,
                    height=45
                ),
                ft.ElevatedButton(
                    "Eliminar Usuario",
                    icon=ft.Icons.DELETE_OUTLINE,
                    bgcolor=styles.BTN_DELETE_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                     on_click=self._delete_handler,
                     height=45
                )
            ]
        )

        self.data_container = ft.Container()

    def refresh_data(self):
        users_data = controller.get_all_users()

        if users_data and len(users_data) > 0:
            rows = []
            for user in users_data:
                nombre_completo = f"{user.nombre} {user.apellidos}"
                # Manejo seguro por si el departamento fue borrado o es nulo
                depto_nombre = user.departamento.nombre if user.departamento else "Sin Asignar"
                
                is_row_selected = (user.id == self.selected_id)
                
                # Obtener valor string del rol
                role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)

                rows.append(
                    ft.DataRow(
                        selected=is_row_selected,
                        on_select_changed=self._handle_select,
                        data=user.id, 
                        cells=[
                            ft.DataCell(ft.Text(user.username, weight=ft.FontWeight.W_500, color=styles.TEXT_COLOR)),
                            ft.DataCell(ft.Text(nombre_completo, color=styles.TEXT_COLOR)),
                            ft.DataCell(ft.Text(depto_nombre, color=styles.TEXT_COLOR)),
                            ft.DataCell(ft.Text(role_str, color=styles.TEXT_COLOR)), # Rol corregido
                        ],
                    )
                )

            self.data_container.alignment = ft.alignment.top_center
            self.data_container.content = ft.Column(
                controls=[
                    ft.Container(
                        bgcolor=ft.Colors.WHITE,
                        border_radius=ft.border_radius.all(12),
                        padding=ft.padding.all(5),
                        content=ft.DataTable(
                            width=float("inf"),
                            heading_row_height=60,
                            data_row_min_height=60,
                            column_spacing=20,
                            show_checkbox_column=False, # Ocultamos checkboxes
                            columns=[
                                ft.DataColumn(ft.Text("USUARIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("NOMBRE COMPLETO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("DEPARTAMENTO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("ROL", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                            ],
                            rows=rows
                        )
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
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