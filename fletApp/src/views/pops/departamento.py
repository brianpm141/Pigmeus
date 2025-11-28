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
        sub_title = "Asigne un nombre y un encargado." if dept_data else "Ingrese los datos del nuevo departamento."
        
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

        # 2. Encargado
        self.manager_dropdown = ft.Dropdown(
            label="Encargado / Responsable",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
        )

        self._load_users_into_dropdown()

        if dept_data:
            self.name_field.value = dept_data.get("nombre")
            self.manager_dropdown.value = str(dept_data.get("lider_id")) if dept_data.get("lider_id") else "none"

        self.content = ft.Column(
            [
                self.name_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.manager_dropdown,
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

    def _load_users_into_dropdown(self):
        users = controller.get_potential_leaders()
        options = []
        if not users:
            options.append(ft.dropdown.Option(key="none", text="No hay usuarios para asignar"))
            self.manager_dropdown.value = "none" 
        else:
            options.append(ft.dropdown.Option(key="none", text="-- Sin Encargado --"))
            for u in users:
                full_name = f"{u.nombre} {u.apellidos}"
                options.append(ft.dropdown.Option(key=str(u.id), text=full_name))
        
        self.manager_dropdown.options = options
        if self.manager_dropdown.page:
            self.manager_dropdown.update()

    def _clear_error_on_type(self, e):
        """Si el usuario escribe, quitamos el rojo"""
        if self.name_field.error_text:
            self.name_field.error_text = None
            self.name_field.update()

    def _save_data(self, e):
        nombre = self.name_field.value
        lider_val = self.manager_dropdown.value

        # Validación Local
        if not nombre or nombre.strip() == "":
            self.name_field.error_text = "El nombre es obligatorio."
            self.name_field.update()
            return

        lider_id = int(lider_val) if lider_val and lider_val != "none" else None

        # Llamar al controlador
        result = None
        if self.dept_data:
            dept_id = self.dept_data.get("id")
            result = controller.update_department(dept_id, nombre, lider_id)
        else:
            result = controller.create_department(nombre, lider_id)
            
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