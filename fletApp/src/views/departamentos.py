import flet as ft
import views.styles as styles
from views.pops.departamento import DepartmentForm
import controllers.departamentos_controller as controller
from views.pops.eliminar import ConfirmationDialog
from views.pops.mensaje import Aviso

class DepartmentsView(ft.Container):
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
        dept_id = e.control.data # Recuperamos el ID guardado en la fila
        
        if is_selected:
            self.selected_id = dept_id # Guardamos el ID seleccionado
        else:
            # Si desmarca el que estaba seleccionado, limpiamos la variable
            if self.selected_id == dept_id:
                self.selected_id = None
        
        # Recargamos la tabla para actualizar visualmente los checkboxes
        # (Para asegurar que solo uno quede marcado a la vez)
        self.refresh_data()

    def _open_create_modal(self, e):
        """Abre modal para crear (sin datos)"""
        form = DepartmentForm(e.page, on_success=self.refresh_data)
        form.open_dialog()

    def _open_modify_modal(self, e):
        """Abre modal para modificar (con datos del seleccionado)"""
        if not self.selected_id:
            self._show_alert("Selecciona un departamento para modificar", is_error=True)
            return

        # Buscamos los datos completos del departamento seleccionado
        # Nota: Podríamos optimizar esto guardando el objeto entero, pero buscarlo es seguro.
        departments = controller.get_all_departments()
        selected_dept = next((d for d in departments if d.id == self.selected_id), None)

        if selected_dept:
            # Convertimos el objeto SQLAlchemy a un diccionario simple para el formulario
            dept_dict = {
                "id": selected_dept.id,
                "nombre": selected_dept.nombre
            }
            
            form = DepartmentForm(e.page, dept_data=dept_dict, on_success=self.refresh_data)
            form.open_dialog()

    def _delete_handler(self, e):
        """Este método se ejecuta al dar clic en el botón de la Toolbar"""
        if not self.selected_id:
            self._show_alert("Selecciona un departamento para eliminar", is_error=True)
            return

        # 2. EN LUGAR DE BORRAR DIRECTO, ABRIMOS EL DIÁLOGO
        dialog = ConfirmationDialog(
            self.page,
            title="Eliminar Departamento",
            content_text="¿Estás seguro de que deseas eliminar este departamento?",
            on_confirm=self._execute_delete # Pasamos la función, NO la llamamos con ()
        )
        dialog.show()

    def _execute_delete(self):
        """Esta es la lógica real que se ejecuta SOLO si confirman"""
        # Llamamos al controlador (Baja Lógica)
        result = controller.delete_department_logical(self.selected_id)
        
        if result["status"] == "success":
            self.selected_id = None # Limpiamos selección
            # Actualizamos la tabla INMEDIATAMENTE para que el usuario vea que desapareció
            self.refresh_data()
            
            # Usamos tu componente Aviso para el éxito
            aviso = Aviso(
                self.page, 
                message=result["message"], # "Departamento eliminado correctamente."
                is_error=False
            )
            aviso.show()
        else:
            # 3. CAMBIO AQUÍ: Usamos tu componente Aviso para el error
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
                    "Crear Departamento",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    bgcolor=styles.BTN_PRIMARY_BG,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=20, vertical=12)
                    ),
                    on_click=self._open_create_modal, # Conectado a crear
                    height=45
                ),
                ft.ElevatedButton(
                    "Modificar Departamento",
                    icon=ft.Icons.EDIT_OUTLINED,
                    bgcolor=styles.BTN_MODIFY_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=self._open_modify_modal, # Conectado a modificar
                    height=45
                ),
                ft.ElevatedButton(
                    "Eliminar Departamento",
                    icon=ft.Icons.DELETE_OUTLINE,
                    bgcolor=styles.BTN_DELETE_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                     on_click=self._delete_handler, # Conectado a eliminar
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
        departments_data = controller.get_all_departments()

        if departments_data and len(departments_data) > 0:
            rows = []
            for dept in departments_data:
                # Solo contamos usuarios activos (status == 1)
                active_users = [u for u in dept.usuarios if u.status == 1] if dept.usuarios else []
                num_usuarios = len(active_users)

                # Determinamos si esta fila debe aparecer marcada
                is_row_selected = (dept.id == self.selected_id)

                rows.append(
                    ft.DataRow(
                        selected=is_row_selected, # Marca visualmente
                        on_select_changed=self._handle_select, # Evento clic
                        data=dept.id, # GUARDAMOS EL ID OCULTO EN LA FILA
                        
                        cells=[
                            ft.DataCell(ft.Text(dept.nombre, weight=ft.FontWeight.W_500, color=styles.TEXT_COLOR)),
                            ft.DataCell(ft.Text(str(num_usuarios), color=styles.TEXT_COLOR)),
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
                        ft.DataColumn(ft.Text("NOMBRE", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("USUARIOS", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
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
                            name=ft.Icons.INBOX_OUTLINED,
                            size=60,
                            color=ft.Colors.GREY_300
                        ),
                        ft.Text(
                            "No hay departamentos registrados.",
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