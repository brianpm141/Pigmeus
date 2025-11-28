import flet as ft
import views.styles as styles

class ConfirmationDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, title: str, content_text: str, on_confirm):
        super().__init__()
        self.page = page
        self.on_confirm_callback = on_confirm

        # --- Configuración Visual ---
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        # --- Contenido ---
        self.title = ft.Text(title, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR)
        self.content = ft.Text(content_text, color=ft.Colors.GREY_700)

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
                "Eliminar",
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.RED_600,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                height=40,
                on_click=self._handle_confirm # Al hacer clic, ejecutamos la lógica interna
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _handle_confirm(self, e):
        """Cierra el diálogo y ejecuta la acción real de borrado"""
        self.close_dialog(None)
        if self.on_confirm_callback:
            self.on_confirm_callback()

    def show(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)