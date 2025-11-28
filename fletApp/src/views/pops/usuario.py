import flet as ft
import views.styles as styles

class UserForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, user_data=None):
        super().__init__()
        self.page = page
        self.user_data = user_data
        
        # --- Configuración ---
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        self.scrollable = True
        
        # --- Título ---
        title_text = "Modificar Usuario" if user_data else "Registrar Nuevo Usuario"
        sub_title = "Edite los datos." if user_data else "Complete la información del colaborador."
        
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
            label="Nombre(s)",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
        )

        # 2. Apellidos
        self.lastname_field = ft.TextField(
            label="Apellidos",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
        )

        # 3. ID
        self.id_field = ft.TextField(
            label="ID de Empleado",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            keyboard_type=ft.KeyboardType.NUMBER
        )

        # 4. Departamento
        self.dept_dropdown = ft.Dropdown(
            label="Departamento",
            width=400,
            options=[
                ft.dropdown.Option("Ingeniería"),
                ft.dropdown.Option("Recursos Humanos"),
                ft.dropdown.Option("Marketing"),
                ft.dropdown.Option("Ventas"),
            ],
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
        )

        # 5. Nivel de Usuario (NUEVO CAMPO)
        self.role_dropdown = ft.Dropdown(
            label="Nivel de Usuario",
            width=400,
            options=[
                ft.dropdown.Option("Básico"),
                ft.dropdown.Option("Gerente"),
                ft.dropdown.Option("Administrador"),
            ],
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            value="Básico" # Valor por defecto opcional
        )

        # --- Pre-llenado (Si es Modificar) ---
        if user_data:
            # self.role_dropdown.value = user_data.get("rol")
            pass

        # --- Contenido ---
        self.content = ft.Column(
            [
                self.name_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.lastname_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.id_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.dept_dropdown,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.role_dropdown, # <--- Agregado aquí
            ],
            width=400,
            height=420, # Aumentamos la altura para que quepa el nuevo campo
            scroll=ft.ScrollMode.AUTO
        )

        # --- Botones ---
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
                "Guardar" if user_data else "Registrar",
                style=ft.ButtonStyle(
                    bgcolor=styles.PRIMARY_BLUE,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                height=40,
                on_click=lambda e: print("Guardando usuario...")
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def open_dialog(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)