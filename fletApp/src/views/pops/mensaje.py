import flet as ft
import views.styles as styles

class Aviso(ft.AlertDialog):
    def __init__(self, page: ft.Page, message: str, is_error: bool = False, on_dismiss=None):
        super().__init__()
        self.page = page
        self.on_dismiss = on_dismiss

        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=12)
        
        # --- AJUSTE VISUAL: Quitamos paddings nativos innecesarios ---
        self.title_padding = 0 
        self.content_padding = ft.padding.all(20) # Un solo padding general
        self.actions_padding = ft.padding.only(bottom=20, left=20, right=20)

        # Configuración de colores e iconos
        if is_error:
            icon_name = ft.Icons.ERROR_OUTLINE
            icon_color = ft.Colors.RED_500
            title_text = "Error"
            btn_color = ft.Colors.RED_500
        else:
            icon_name = ft.Icons.CHECK_CIRCLE_OUTLINE
            icon_color = ft.Colors.GREEN_500
            title_text = "Éxito"
            btn_color = styles.PRIMARY_BLUE

        # --- ESTRATEGIA COMPACTA: Todo en una sola columna ---
        # Al poner todo en 'content', controlamos nosotros mismos el espacio
        self.title = None 

        self.content = ft.Column(
            tight=True, # <--- ESTO ES LA CLAVE: La columna se encoge al tamaño del contenido
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10, # Espacio controlado entre elementos
            controls=[
                # 1. Icono
                ft.Icon(icon_name, size=50, color=icon_color),
                # 2. Título
                ft.Text(title_text, weight=ft.FontWeight.BOLD, size=20, color=styles.TEXT_COLOR),
                # 3. Mensaje
                ft.Text(
                    message, 
                    text_align=ft.TextAlign.CENTER, 
                    size=15, 
                    color=ft.Colors.GREY_700
                ),
            ]
        )

        # --- Botón ---
        self.actions = [
            ft.Container(
                content=ft.ElevatedButton(
                    "Entendido",
                    style=ft.ButtonStyle(
                        bgcolor=btn_color,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=30, vertical=12)
                    ),
                    on_click=self.close_dialog
                ),
                alignment=ft.alignment.center,
            )
        ]
        self.actions_alignment = ft.MainAxisAlignment.CENTER

    def show(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)
        if self.on_dismiss:
            self.on_dismiss(e)