import flet as ft
import views.styles as styles
import controllers.departamentos_controller as controller
from views.pops.mensaje import Aviso

class DepartmentForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, dept_data=None, on_success=None):
        super().__init__()
        self.page = page
        self.dept_data = dept_data
        self.on_success = on_success 
        
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        title_text = "Modificar Departamento" if dept_data else "Crear Departamento"
        sub_title = "Asigne un nombre." if dept_data else "Ingrese los datos del nuevo departamento."
        
        self.title = ft.Column(
            [
                ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Text(sub_title, size=12, color=ft.Colors.GREY_500),
            ],
            spacing=5
        )

        # --- Campos ---
        
        # 1. Nombre del Departamento
        self.name_field = ft.TextField(
            label="Nombre del Departamento",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            hint_text="Ej. Recursos Humanos",
            # MEJORA 1: Limpiar el error cuando el usuario escriba
            on_change=self._clear_error_on_type 
        )

        # 2. Código (Nuevo)
        self.code_field = ft.TextField(
            label="Código (Acceso General)",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            hint_text="Ej. 1234 (Máx 5 dígitos)",
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
            max_length=5,
            on_change=self._clear_error_on_type
        )

        if dept_data:
            self.name_field.value = dept_data.get("nombre")
            self.code_field.value = str(dept_data.get("code") or "")

        self.content = ft.Column(
            [
                self.name_field,
                self.code_field
            ],
            width=400,
            height=200, # Aumentar altura
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
                "Guardar" if dept_data else "Crear",
                style=ft.ButtonStyle(
                    bgcolor=styles.PRIMARY_BLUE,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                height=40,
                on_click=self._save_data 
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _clear_error_on_type(self, e):
        """Si el usuario escribe, quitamos el rojo"""
        if e.control.error_text:
            e.control.error_text = None
            e.control.update()

    def _save_data(self, e):
        nombre = self.name_field.value
        code_str = self.code_field.value

        # Validación Local
        has_error = False
        
        if not nombre or nombre.strip() == "":
            self.name_field.error_text = "El nombre es obligatorio."
            has_error = True
            
        if not code_str:
            self.code_field.error_text = "El código es obligatorio."
            has_error = True
            
        if has_error:
            self.page.update()
            return
            
        # Convertir a int
        try:
            code_int = int(code_str)
        except ValueError:
            self.code_field.error_text = "Debe ser numérico."
            self.code_field.update()
            return

        # Llamar al controlador
        result = None
        if self.dept_data:
            dept_id = self.dept_data.get("id")
            result = controller.update_department(dept_id, nombre, code_int)
        else:
            result = controller.create_department(nombre, code_int)
            
        # --- AQUI ES EL CAMBIO PRINCIPAL ---
        if result["status"] == "success":
            # 1. Cerramos el formulario actual
            self.close_dialog(None)
            
            # 2. Definimos qué hacer cuando el usuario cierre el Aviso de éxito
            def on_aviso_close(e):
                if self.on_success:
                    self.on_success() # Refrescar la tabla
            
            # 3. Mostramos el Aviso de Éxito
            aviso = Aviso(
                self.page, 
                message=result["message"], 
                is_error=False,
                on_dismiss=on_aviso_close
            )
            aviso.show()
            
        else:
            # Si es un error de duplicado, lo mostramos en el campo (mejor UX)
            if "existe" in result["message"].lower():
                self.name_field.error_text = result["message"]
                self.name_field.update()
            else:
                # Si es otro tipo de error (ej. base de datos caída), mostramos el Aviso Rojo
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