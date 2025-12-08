import flet as ft
import views.styles as styles

class LoadingView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.bgcolor = styles.BG_COLOR
        self.alignment = ft.alignment.center
        self.animate_opacity = 500  # 500ms fade animation

        self.msg = ft.Text(
            "Conectando a la base de datos...",
            size=16,
            color=styles.TEXT_COLOR,
            weight=ft.FontWeight.W_500,
            font_family="Poppins"
        )

        self.content = ft.Column(
            controls=[
                ft.Image(
                    src="img/pigmeus.png",
                    width=200,
                    height=200,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Container(height=10), # Spacer
                ft.ProgressRing(
                    color=styles.PRIMARY_BLUE, 
                    width=30, 
                    height=30, 
                    stroke_width=3
                ),
                self.msg,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

