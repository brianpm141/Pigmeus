import flet as ft
import views.styles as styles
import controllers.categorias_controller as cat_controller
import controllers.departamentos_controller as dept_controller
from views.pops.mensaje import Aviso

class CategoryForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, category_data=None, on_success=None):
        super().__init__()
        self.page = page
        self.category_data = category_data
        self.on_success = on_success
        
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        title_text = "Modificar Categoría" if category_data else "Crear Categoría"
        sub_title = "Edite los datos." if category_data else "Ingrese los datos de la nueva categoría."
        
        self.title = ft.Column(
            [
                ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Text(sub_title, size=12, color=ft.Colors.GREY_500),
            ],
            spacing=5
        )

        # --- Campos ---
        
        # 1. Nombre
        self.name_field = ft.TextField(
            label="Nombre de la Categoría",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error_on_type
        )

        # 2. Departamento (Dinámico)
        depts = dept_controller.get_all_departments()
        dept_options = [ft.dropdown.Option(key=d.id, text=d.nombre) for d in depts]

        self.dept_dropdown = ft.Dropdown(
            label="Departamento",
            width=400,
            options=dept_options,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error_on_type
        )

        # --- Pre-llenado ---
        if category_data:
            self.name_field.value = category_data.get("nombre", "")
            self.dept_dropdown.value = category_data.get("departamento_id")

        self.content = ft.Column(
            [
                self.name_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.dept_dropdown,
            ],
            width=400,
            height=180,
            scroll=ft.ScrollMode.AUTO
        )

        self.actions = [
            ft.OutlinedButton(
                "Cancelar",
                style=ft.ButtonStyle(
                    color=styles.TEXT_COLOR,
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(width=1, color=ft.Colors.GREY_300)
                ),
                height=40,
                on_click=self.close_dialog
            ),
            ft.ElevatedButton(
                "Guardar" if category_data else "Crear",
                style=ft.ButtonStyle(
                    bgcolor=styles.PRIMARY_BLUE,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                height=40,
                on_click=self._save
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _clear_error_on_type(self, e):
        if e.control.error_text:
            e.control.error_text = None
            e.control.update()

    def _save(self, e):
        # Validaciones
        has_error = False
        
        if not self.name_field.value:
            self.name_field.error_text = "Campo obligatorio"
            has_error = True
            
        if not self.dept_dropdown.value:
            self.dept_dropdown.error_text = "Seleccione un departamento"
            has_error = True
            self.dept_dropdown.update()

        if has_error:
            self.update()
            return

        data = {
            "nombre": self.name_field.value,
            "dept_id": int(self.dept_dropdown.value),
        }

        if self.category_data:
            result = cat_controller.update_category(self.category_data["id"], **data)
        else:
            result = cat_controller.create_category(**data)

        if result["status"] == "success":
            self.close_dialog(None)
            
            def on_aviso_close(e):
                if self.on_success:
                    self.on_success()
            
            aviso = Aviso(
                self.page, 
                message=result["message"], 
                is_error=False,
                on_dismiss=on_aviso_close
            )
            aviso.show()
        else:
            aviso = Aviso(
                self.page, 
                message=result["message"], 
                is_error=True
            )
            aviso.show()

    def open_dialog(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)
