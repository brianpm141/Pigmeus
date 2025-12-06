import flet as ft
import views.styles as styles
from controllers.usuarios_controller import get_all_users
from controllers.actividades_controller import create_activity, update_activity
from controllers.categorias_controller import get_all_categories
from views.pops.mensaje import Aviso

class ActivityForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, activity_data=None, on_success=None):
        super().__init__()
        self.page = page
        self.activity_data = activity_data
        self.on_success = on_success
        
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        # Cargar datos
        self.users = get_all_users()
        self.categories = get_all_categories() 
        
        # --- CAMPOS ---
        
        # 1. Usuario (Dropdown)
        self.user_dropdown = ft.Dropdown(
            label="Usuario",
            width=400,
            options=[ft.dropdown.Option(key=str(u.id), text=f"{u.nombre} {u.apellidos}") for u in self.users],
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error
        )

        # 2. Contraseña (TextField)
        self.password_field = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error
        )

        # 3. Categoría (Dropdown)
        cat_options = []
        if self.categories:
             cat_options = [ft.dropdown.Option(key=str(c.id), text=c.nombre) for c in self.categories]
        else:
             cat_options = [ft.dropdown.Option(key="1", text="General")]

        self.category_dropdown = ft.Dropdown(
            label="Categoría",
            width=400,
            options=cat_options,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error
        )

        # 4. Detalles
        self.details_field = ft.TextField(
            label="Detalles",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error
        )

        # 5. Estado
        self.status_badge = ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=ft.border_radius.all(15),
            alignment=ft.alignment.center
        )
        self.status_text = ft.Text(size=12, weight=ft.FontWeight.BOLD)
        self.status_badge.content = self.status_text

        self.status_switch = ft.Switch(
            on_change=self._on_status_change,
            active_color=styles.STATUS_GREEN_TXT,
        )
        self._update_status_visuals(is_completed=False)

        # --- PRE-LLENADO (Modificar) ---
        if activity_data:
            # Usuario
            user_id = activity_data.get("usuario_id")
            if user_id:
                self.user_dropdown.value = str(user_id)
                self.user_dropdown.disabled = True # No permitir cambiar usuario
                self.password_field.visible = False # No pedir password al modificar
            
            # Categoría
            cat_id = activity_data.get("categoria")
            if cat_id:
                self.category_dropdown.value = str(cat_id)
            
            # Detalles
            self.details_field.value = activity_data.get("detalles", "")
            
            # Estado
            is_completed = activity_data.get("estado") == "Completada"
            self.status_switch.value = is_completed
            self._update_status_visuals(is_completed)

        # --- CONTENIDO ---
        title_text = "Modificar Actividad" if activity_data else "Registrar Actividad"
        self.title = ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR)
        
        form_controls = [
            self.user_dropdown,
            self.password_field if not activity_data else ft.Container(), # Ocultar visualmente si es modificar
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.category_dropdown,
            self.details_field,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Row([ft.Text("Estado:", color=styles.TEXT_COLOR), self.status_switch, self.status_badge]),
        ]

        self.content = ft.Column(
            form_controls,
            width=400,
            height=450,
            scroll=ft.ScrollMode.AUTO
        )

        # --- BOTONES ---
        self.actions = [
            ft.OutlinedButton("Cancelar", on_click=self.close_dialog),
            ft.ElevatedButton(
                "Guardar" if activity_data else "Registrar",
                bgcolor=styles.PRIMARY_BLUE,
                color=ft.Colors.WHITE,
                on_click=self._save_activity
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _update_status_visuals(self, is_completed):
        if is_completed:
            self.status_text.value = "Completada"
            self.status_text.color = styles.STATUS_GREEN_TXT
            self.status_badge.bgcolor = styles.STATUS_GREEN_BG
        else:
            self.status_text.value = "Pendiente"
            self.status_text.color = styles.STATUS_YELLOW_TXT
            self.status_badge.bgcolor = styles.STATUS_YELLOW_BG

    def _on_status_change(self, e):
        self._update_status_visuals(self.status_switch.value)
        self.status_badge.update()

    def _clear_error(self, e):
        if e.control.error_text:
            e.control.error_text = None
            e.control.update()

    def _save_activity(self, e):
        status_str = "Completada" if self.status_switch.value else "Pendiente"
        
        has_error = False
        
        # Validaciones comunes
        if not self.category_dropdown.value:
            self.category_dropdown.error_text = "Requerido"
            has_error = True

        # Lógica UPDATE
        if self.activity_data:
            if has_error:
                self.page.update()
                return
            
            res = update_activity(
                activity_id=self.activity_data["id"],
                category_id=int(self.category_dropdown.value),
                details=self.details_field.value,
                status_str=status_str
            )
        
        # Lógica CREATE
        else:
            if not self.user_dropdown.value:
                self.user_dropdown.error_text = "Requerido"
                has_error = True
            
            if not self.password_field.value:
                self.password_field.error_text = "Requerida"
                has_error = True
                
            if has_error:
                self.page.update()
                return

            res = create_activity(
                user_id=int(self.user_dropdown.value),
                password_attempt=self.password_field.value,
                category_id=int(self.category_dropdown.value),
                details=self.details_field.value,
                status_str=status_str
            )

        if res["status"] == "success":
            self.close_dialog(None)
            Aviso(self.page, res["message"]).show()
            if self.on_success:
                self.on_success()
        else:
            # Manejo de errores específicos del controlador
            msg = res["message"].lower()
            if "contraseña" in msg:
                self.password_field.error_text = res["message"]
                self.password_field.update()
            elif "usuario" in msg:
                self.user_dropdown.error_text = res["message"]
                self.user_dropdown.update()
            else:
                Aviso(self.page, res["message"], is_error=True).show()

    def open_dialog(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)