import flet as ft
import views.styles as styles

class ActivityForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, activity_data=None):
        super().__init__()
        self.page = page
        self.activity_data = activity_data  # Si es None = Crear, Si tiene datos = Modificar
        
        # Configuración básica del Dialog
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        # --- CAMPOS DEL FORMULARIO ---
        
        # 1. Título dinámico
        title_text = "Modificar actividad" if activity_data else "Registrar nueva actividad"
        sub_title = "Edite los detalles de la actividad." if activity_data else "Complete los detalles de la nueva actividad."
        
        self.title = ft.Column(
            [
                ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Text(sub_title, size=12, color=ft.Colors.GREY_500),
            ],
            spacing=5
        )

        # 2. Categoría (Dropdown)
        self.category_dropdown = ft.Dropdown(
            label="Categoría",
            width=400,
            options=[
                ft.dropdown.Option("Reunión"),
                ft.dropdown.Option("Llamada"),
                ft.dropdown.Option("Desarrollo"),
            ],
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
        )

        # 3. Detalles (Campo de texto multilínea)
        self.details_field = ft.TextField(
            label="Detalles",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
        )

        # 4. Estado (Switch con etiqueta dinámica)
        # Etiqueta visual del estado (Badge)
        self.status_badge = ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=ft.border_radius.all(15),
            alignment=ft.alignment.center
        )
        self.status_text = ft.Text(size=12, weight=ft.FontWeight.BOLD)
        self.status_badge.content = self.status_text

        # Switch lógico
        self.status_switch = ft.Switch(
            on_change=self._on_status_change,
            active_color=styles.STATUS_GREEN_TXT,
        )

        # Inicializamos el estado visual del switch
        self._update_status_visuals(is_completed=False) # Por defecto Pendiente

        # --- PRE-LLENADO DE DATOS (Si es modificar) ---
        if activity_data:
            self.category_dropdown.value = activity_data.get("categoria", "")
            self.details_field.value = activity_data.get("detalles", "")
            # Si el dato dice "Completada", activamos el switch
            is_completed = activity_data.get("estado") == "Completada"
            self.status_switch.value = is_completed
            self._update_status_visuals(is_completed)

        # --- CONTENIDO DEL DIALOG ---
        self.content = ft.Column(
            [
                self.category_dropdown,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.details_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text("Estado", color=styles.TEXT_COLOR, weight=ft.FontWeight.W_500),
                ft.Row(
                    [
                        self.status_switch,
                        self.status_badge # Mostramos el badge al lado del switch
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            width=400,
            height=320, # Altura fija para evitar saltos
            scroll=ft.ScrollMode.AUTO
        )

        # --- BOTONES DE ACCIÓN ---
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
                "Registrar" if not activity_data else "Guardar Cambios",
                style=ft.ButtonStyle(
                    bgcolor=styles.PRIMARY_BLUE,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                height=40,
                on_click=lambda e: print("Guardando datos...") # Lógica futura
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _update_status_visuals(self, is_completed):
        """Actualiza el color y texto del badge según el estado"""
        if is_completed:
            self.status_text.value = "Completada"
            self.status_text.color = styles.STATUS_GREEN_TXT
            self.status_badge.bgcolor = styles.STATUS_GREEN_BG
        else:
            self.status_text.value = "Pendiente"
            self.status_text.color = styles.STATUS_YELLOW_TXT
            self.status_badge.bgcolor = styles.STATUS_YELLOW_BG
        
    def _on_status_change(self, e):
        """Evento al mover el switch"""
        self._update_status_visuals(self.status_switch.value)
        self.status_badge.update()

    def open_dialog(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)