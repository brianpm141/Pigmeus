import flet as ft
import views.styles as styles
import views.actividades as actividades
import views.departamentos as departamentos

class Sidebar(ft.Container):
    def __init__(self, on_nav_change):
        super().__init__()
        self.on_nav_change = on_nav_change 

        self.nav_items={}

        #---------------------Contenido---------------------
        self.width = 250
        self.bgcolor = styles.SIDEBAR_BG
        self.padding = ft.padding.all(20)
        self.border = ft.border.only(
            right=ft.BorderSide(width=1, color=ft.Colors.GREY_200)
        )
        self.content = self._build_content()

    def _highlight_item(self, selected_text):
        """Recorre todos los items y actualiza sus estilos según la selección"""
        for text, item_container in self.nav_items.items():
            is_selected = (text == selected_text)
            
            # Cambiar fondo del contenedor
            item_container.bgcolor = styles.PRIMARY_BLUE if is_selected else ft.Colors.TRANSPARENT
            
            # Accedemos a los hijos del Row (Icono y Texto) para cambiar sus colores
            icon = item_container.content.controls[0]
            label = item_container.content.controls[1]
            
            icon.color = ft.Colors.WHITE if is_selected else styles.TEXT_COLOR
            label.color = ft.Colors.WHITE if is_selected else styles.TEXT_COLOR
            label.weight = ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL
            
            # Actualizamos el contenedor visualmente
            item_container.update()

    def _on_item_click(self, text):
        """Maneja el clic: navega y cambia el estilo"""
        self.on_nav_change(text) # Cambia la vista en el main
        self._highlight_item(text)


    def _build_item(self, icon, text, is_selected=False):
        # Creamos el contenedor del item
        item = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        name=icon,
                        color=ft.Colors.WHITE if is_selected else styles.TEXT_COLOR,
                        size=20
                    ),
                    ft.Text(
                        value=text,
                        color=ft.Colors.WHITE if is_selected else styles.TEXT_COLOR,
                        weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL
                    ),
                ],
                spacing=15,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=ft.border_radius.all(10),
            bgcolor=styles.PRIMARY_BLUE if is_selected else ft.Colors.TRANSPARENT,
            ink=True,
            # Al hacer clic, llamamos a nuestro manejador interno
            on_click=lambda e: self._on_item_click(text)
        )
        
        # 2. Guardamos la referencia usando el texto como llave
        self.nav_items[text] = item
        return item

    def _build_content(self):
        return ft.Column(
            controls=[
                # Logo
                ft.Row(
                    [
                        ft.Image(
                            src="img/pigmeus.png",
                            width=30,
                            height=30,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        ft.Text("Pigmeus App", size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                    ],
                    spacing=10,
                ),
                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),

                # Menú
                self._build_item(ft.Icons.CHECKLIST_RTL_ROUNDED, "Actividades", is_selected=True),
                self._build_item(ft.Icons.LAYERS_OUTLINED, "Proyectos"),
                self._build_item(ft.Icons.ASSIGNMENT_OUTLINED, "Departamentos"),
                self._build_item(ft.Icons.ASSIGNMENT_OUTLINED, "Usuarios"),
            ],
            spacing=5,
        )