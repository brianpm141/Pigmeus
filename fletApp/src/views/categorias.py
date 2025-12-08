import flet as ft
import views.styles as styles
from views.pops.categoria import CategoryForm
import controllers.categorias_controller as controller
from views.pops.eliminar import ConfirmationDialog
from views.pops.mensaje import Aviso

class CategoriesView(ft.Container):
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
        
        self.selected_id = None 
        
        self.refresh_data()

    # --- MANEJADORES DE EVENTOS ---

    def _handle_select(self, e):
        is_selected = e.data == "true"
        cat_id = e.control.data 
        
        if is_selected:
            self.selected_id = cat_id 
        else:
            if self.selected_id == cat_id:
                self.selected_id = None
        
        self.refresh_data()

    def _open_create_modal(self, e):
        def on_success():
            self.selected_id = None
            self.refresh_data()
            
        form = CategoryForm(e.page, on_success=on_success)
        form.open_dialog()

    def _open_modify_modal(self, e):
        if not self.selected_id:
            self._show_alert("Selecciona una categoría para modificar", is_error=True)
            return

        categories = controller.get_all_categories()
        selected_cat = next((c for c in categories if c.id == self.selected_id), None)

        if selected_cat:
            cat_dict = {
                "id": selected_cat.id,
                "nombre": selected_cat.nombre,
                "departamento_id": selected_cat.departamento_id,
            }
            
            def on_success():
                self.selected_id = None
                self.refresh_data()

            form = CategoryForm(e.page, category_data=cat_dict, on_success=on_success)
            form.open_dialog()

    def _delete_handler(self, e):
        if not self.selected_id:
            self._show_alert("Selecciona una categoría para eliminar", is_error=True)
            return

        dialog = ConfirmationDialog(
            self.page,
            title="Eliminar Categoría",
            content_text="¿Estás seguro de que deseas eliminar esta categoría?",
            on_confirm=self._execute_delete
        )
        dialog.show()

    def _execute_delete(self):
        result = controller.delete_category_logical(self.selected_id)
        
        if result["status"] == "success":
            self.selected_id = None 
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
        color = ft.Colors.RED if is_error else ft.Colors.GREEN
        self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    # --- CONSTRUCCIÓN DE UI ---

    def _init_layout_components(self):
        
        self.toolbar = ft.Row(
            wrap=True,
            spacing=15,
            controls=[
                ft.ElevatedButton(
                    "Crear Categoría",
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
                    "Modificar Categoría",
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
                    "Eliminar Categoría",
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
        categories = controller.get_all_categories()

        if categories and len(categories) > 0:
            rows = []
            for cat in categories:
                dept_nombre = cat.departamento_rel.nombre if cat.departamento_rel else "Sin Departamento"
                
                is_row_selected = (cat.id == self.selected_id)

                rows.append(
                    ft.DataRow(
                        selected=is_row_selected, 
                        on_select_changed=self._handle_select, 
                        data=cat.id, 
                        
                        cells=[
                            ft.DataCell(ft.Text(cat.nombre, weight=ft.FontWeight.W_500, color=styles.TEXT_COLOR)),
                            ft.DataCell(ft.Text(dept_nombre, color=styles.TEXT_COLOR)),
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
                            show_checkbox_column=False,
                            columns=[
                                ft.DataColumn(ft.Text("NOMBRE", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("DEPARTAMENTO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                            ],
                            rows=rows
                        )
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            self.data_container.alignment = ft.alignment.center
            self.data_container.content = ft.Column(
                controls=[
                    ft.Icon(
                        name=ft.Icons.CATEGORY_OUTLINED,
                        size=60,
                        color=ft.Colors.GREY_300
                    ),
                    ft.Text(
                        "No hay categorías registradas.",
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
