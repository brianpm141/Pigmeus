import flet as ft
import views.styles as styles
from views.pops.usuario import UserForm
import controllers.usuarios_controller as controller
from views.pops.eliminar import ConfirmationDialog
from views.pops.mensaje import Aviso

class UsersView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            controls=self._build_layout(),
        )
        
        # VARIABLE DE ESTADO: Guarda el ID del elemento seleccionado
        self.selected_id = None 
        
        self.refresh_data()

    # --- MANEJADORES DE EVENTOS ---

    def _handle_select(self, e):
        """Maneja la selección de filas (Lógica de selección única)"""
        is_selected = e.data == "true"
        user_id = e.control.data # Recuperamos el ID guardado en la fila
        
        if is_selected:
            self.selected_id = user_id # Guardamos el ID seleccionado
        else:
            # Si desmarca el que estaba seleccionado, limpiamos la variable
            if self.selected_id == user_id:
                self.selected_id = None
        
        # Recargamos la tabla para actualizar visualmente los checkboxes
        self.refresh_data()

    def _open_create_modal(self, e):
        """Abre modal para crear (sin datos)"""
        form = UserForm(e.page, on_success=self.refresh_data)
        form.open_dialog()

    def _open_modify_modal(self, e):
        """Abre modal para modificar (con datos del seleccionado)"""
        if not self.selected_id:
            self._show_alert("Selecciona un usuario para modificar", is_error=True)
            return

        # Buscamos los datos completos del usuario seleccionado
        users = controller.get_all_users()
        selected_user = next((u for u in users if u.id == self.selected_id), None)

        if selected_user:
            # Convertimos el objeto SQLAlchemy a un diccionario simple para el formulario
            user_dict = {
                "id": selected_user.id,
                "nombre": selected_user.nombre,
                "apellidos": selected_user.apellidos,
                "user": selected_user.user,
                "departamento_id": selected_user.departamento_id,
                "role": selected_user.role
            }
            
            form = UserForm(e.page, user_data=user_dict, on_success=self.refresh_data)
            form.open_dialog()

    def _delete_handler(self, e):
        """Este método se ejecuta al dar clic en el botón de la Toolbar"""
        if not self.selected_id:
            self._show_alert("Selecciona un usuario para eliminar", is_error=True)
            return

        dialog = ConfirmationDialog(
            self.page,
            title="Eliminar Usuario",
            content_text="¿Estás seguro de que deseas eliminar este usuario?",
            on_confirm=self._execute_delete
        )
        dialog.show()

    def _execute_delete(self):
        """Esta es la lógica real que se ejecuta SOLO si confirman"""
        result = controller.delete_user_logical(self.selected_id)
        
        if result["status"] == "success":
            self.selected_id = None # Limpiamos selección
            self.refresh_data()
            
            aviso = Aviso(
                self.page, 
                message=result["message"], 
                is_error=False
            )
            aviso.show()
        else:
            aviso = Aviso(
                self.page, 
                message=result["message"], 
                is_error=True
            )
            aviso.show()

    def _show_alert(self, message, is_error=False):
        """Helper para mostrar SnackBars"""
        color = ft.Colors.RED if is_error else ft.Colors.GREEN
        self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    # --- CONSTRUCCIÓN DE UI ---

    def _build_layout(self):
        
        self.toolbar = ft.Row(
            wrap=True,
            spacing=15,
            controls=[
                ft.ElevatedButton(
                    "Crear Usuario",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    bgcolor=styles.PRIMARY_BLUE,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=20, vertical=12)
                    ),
                    on_click=self._open_create_modal,
                    height=45
                ),
                ft.OutlinedButton(
                    "Modificar Usuario",
                    icon=ft.Icons.EDIT_OUTLINED,
                    style=ft.ButtonStyle(
                        color=styles.TEXT_COLOR,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(width=1, color=ft.Colors.GREY_300),
                        overlay_color=ft.Colors.GREY_100,
                    ),
                    on_click=self._open_modify_modal,
                    height=45
                ),
                ft.OutlinedButton(
                    "Eliminar Usuario",
                    icon=ft.Icons.DELETE_OUTLINE,
                    style=ft.ButtonStyle(
                        color=ft.Colors.RED_500,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(width=1, color=ft.Colors.RED_200),
                        overlay_color=ft.Colors.RED_50,
                    ),
                     on_click=self._delete_handler,
                     height=45
                )
            ]
        )

        self.data_container = ft.Container()

        return [
            self.toolbar,
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            self.data_container
        ]

    def refresh_data(self):
        users_data = controller.get_all_users()

        if users_data and len(users_data) > 0:
            rows = []
            for user in users_data:
                nombre_completo = f"{user.nombre} {user.apellidos}"
                depto_nombre = user.departamento.nombre if user.departamento else "Sin Asignar"
                
                # Determinamos si esta fila debe aparecer marcada
                is_row_selected = (user.id == self.selected_id)

                rows.append(
                    ft.DataRow(
                        selected=is_row_selected, # Marca visualmente
                        on_select_changed=self._handle_select, # Evento clic
                        data=user.id, # GUARDAMOS EL ID OCULTO EN LA FILA
                        
                        cells=[
                            ft.DataCell(ft.Text(user.user, weight=ft.FontWeight.W_500, color=styles.TEXT_COLOR)),
                            ft.DataCell(ft.Text(nombre_completo, color=styles.TEXT_COLOR)),
                            ft.DataCell(ft.Text(depto_nombre, color=styles.TEXT_COLOR)),
                            ft.DataCell(ft.Text(self._get_role_name(user.role), color=styles.TEXT_COLOR)),
                        ],
                    )
                )

            self.data_container.content = ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.all(12),
                padding=ft.padding.all(5),
                content=ft.DataTable(
                    width=float("inf"),
                    heading_row_height=60,
                    data_row_min_height=60,
                    column_spacing=20,
                    # Habilitamos la columna de checkboxes nativa
                    show_checkbox_column=False,
                    columns=[
                        ft.DataColumn(ft.Text("ID USUARIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("NOMBRE", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("DEPARTAMENTO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("ROL", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                    ],
                    rows=rows
                )
            )
        else:
            self.data_container.content = ft.Container(
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=50),
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.PERSON_OFF_OUTLINED,
                            size=60,
                            color=ft.Colors.GREY_300
                        ),
                        ft.Text(
                            "No hay usuarios registrados.",
                            color=ft.Colors.GREY_500,
                            size=16
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
            )
        
        if self.data_container.page:
            self.data_container.update()

    def _get_role_name(self, role_id):
        role_map = {1: "Básico", 2: "Gerente", 3: "Administrador"}
        return role_map.get(role_id, "Desconocido")