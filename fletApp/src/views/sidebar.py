import flet as ft
import views.styles as styles
import views.actividades as actividades
import views.departamentos as departamentos
import views.categorias as categorias

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
            item_container.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.WHITE) if is_selected else ft.Colors.TRANSPARENT
            
            # Accedemos a los hijos del Row (Icono y Texto) para cambiar sus colores
            icon = item_container.content.controls[0]
            label = item_container.content.controls[1]
            
            icon.color = styles.SIDEBAR_ICON_SELECTED if is_selected else styles.SIDEBAR_TEXT
            label.color = styles.SIDEBAR_TEXT_SELECTED if is_selected else styles.SIDEBAR_TEXT
            label.weight = ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL
            
            item_container.update()

    def _on_item_click(self, text):
        self.on_nav_change(text)
        self._highlight_item(text)

    def _build_item(self, icon, text, is_selected=False):
        item = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        name=icon,
                        color=styles.SIDEBAR_ICON_SELECTED if is_selected else styles.SIDEBAR_TEXT,
                        size=20
                    ),
                    ft.Text(
                        value=text,
                        color=styles.SIDEBAR_TEXT_SELECTED if is_selected else styles.SIDEBAR_TEXT,
                        weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL,
                        size=14
                    ),
                ],
                spacing=15,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=ft.border_radius.all(10),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE) if is_selected else ft.Colors.TRANSPARENT,
            ink=True,
            on_click=lambda e: self._on_item_click(text)
        )
        
        self.nav_items[text] = item
        return item

    def _build_content(self):
        return ft.Column(
            controls=[
                # Logo
                ft.Container(
                    padding=ft.padding.only(bottom=20),
                    content=ft.Image(
                        src="img/logoNameFlat.png",
                        fit=ft.ImageFit.FIT_WIDTH,
                    ),
                ),
                
                # Menú
                self._build_item(ft.Icons.TASK_ALT, "Actividades", is_selected=True),
                self._build_item(ft.Icons.ROCKET_LAUNCH_OUTLINED, "Proyectos"),
                self._build_item(ft.Icons.BUSINESS, "Departamentos"),
                self._build_item(ft.Icons.PEOPLE_OUTLINE, "Usuarios"),
                self._build_item(ft.Icons.CATEGORY_OUTLINED, "Categorias"),
            ],
            spacing=10,
        )