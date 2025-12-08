import flet as ft
import views.styles as styles

class LoadingView(ft.Container):
    def __init__(self, message="Conectando a la base de datos..."):
        super().__init__()
        self.expand = True
        self.bgcolor = styles.BG_COLOR
        self.alignment = ft.alignment.center
        self.animate_opacity = 500  # 500ms fade animation

        self.msg = ft.Text(
            message,
            size=16,
            color=styles.TEXT_COLOR,
            weight=ft.FontWeight.W_500,
            font_family="Poppins"
        )

        self.logo_img = ft.Image(
            src="img/logoName.png",
            width=400,
            height=400,
            fit=ft.ImageFit.CONTAIN,
            scale=0.8, # Start slightly smaller
            animate_scale=ft.Animation(800, ft.AnimationCurve.ELASTIC_OUT)
        )

        self.content = ft.Column(
            controls=[
                self.logo_img,
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

    def did_mount(self):
        # Auto-trigger pulse on mount logic if needed, 
        # but since we use python sleep in main, this might be tricky.
        # instead we can rely on main calling a method or just the initial state.
        pass

    def animate_in(self):
        self.logo_img.scale = 1.0
        self.logo_img.update()

