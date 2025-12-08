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

    def _init_layout_components(self):
        # Título
        self.header = ft.Text("Departamentos", size=24, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR)

        # Toolbar con botones expandidos
        self.toolbar = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Crear Departamento",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    bgcolor=styles.BTN_PRIMARY_BG,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(vertical=20) # Más alto
                    ),
                    on_click=self._open_create_modal,
                    expand=1 # Ocupa 1/4 del ancho disponible (3 botones + 1 espacio)
                ),
                ft.ElevatedButton(
                    "Modificar Departamento",
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
                    "Eliminar Departamento",
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
                # Espacio a la derecha
                ft.Container(expand=1)
            ],
            spacing=15, # Espacio entre botones
        )

        self.data_container = ft.Container()

    def _build_card(self, dept):
        is_selected = (dept.id == self.selected_id)
        
        # Contar usuarios
        active_users = [u for u in dept.usuarios if u.status == 1] if dept.usuarios else []
        num_usuarios = len(active_users)
        subtitle = f"{num_usuarios} Usuario{'s' if num_usuarios != 1 else ''}"

        return ft.Container(
            content=ft.Row(
                controls=[
                    # Icono
                    ft.Container(
                        content=ft.Icon(ft.Icons.CODE, color=ft.Colors.GREY_600), # Icono genérico o específico
                        padding=15,
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=10,
                    ),
                    # Textos
                    ft.Column(
                        controls=[
                            ft.Text(dept.nombre, weight=ft.FontWeight.BOLD, size=16, color=styles.TEXT_COLOR),
                            ft.Text(subtitle, size=13, color=ft.Colors.GREY_500),
                        ],
                        spacing=2,
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
            on_click=lambda e: self._on_card_click(dept.id),
            ink=True
        )

    def _on_card_click(self, dept_id):
        if self.selected_id == dept_id:
            self.selected_id = None
        else:
            self.selected_id = dept_id
        self.refresh_data()

    def refresh_data(self):
        departments_data = controller.get_all_departments()

        if departments_data and len(departments_data) > 0:
            cards = []
            for dept in departments_data:
                cards.append(self._build_card(dept))

            self.data_container.alignment = ft.alignment.top_center
            self.data_container.content = ft.ListView(
                controls=cards,
                spacing=15, # Espacio entre cards
                padding=ft.padding.only(bottom=20)
            )
        else:
            self.data_container.alignment = ft.alignment.center
            self.data_container.content = ft.Column(
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
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
        
        if self.data_container.page:
            self.data_container.update()