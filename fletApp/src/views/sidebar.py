import flet as ft
import views.styles as styles
import views.actividades as actividades
import views.departamentos as departamentos
import views.categorias as categorias

from db.models import Usuario, Departamento, UserRole

class Sidebar(ft.Container):
    def __init__(self, on_nav_change, current_user, on_logout):
        super().__init__()
        self.on_nav_change = on_nav_change 
        self.current_user = current_user
        self.on_logout = on_logout
        
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
        # 1. Determinar nivel de acceso
        # Acciones disponibles:
        # - Actividades (Todos)
        # - Proyectos (Todos)
        # - Usuarios (Gerente, Admin)
        # - Categorias (Gerente, Admin)
        # - Departamentos (Admin)
        
        show_admin_items = False
        show_manager_items = False
        
        if isinstance(self.current_user, Usuario):
            role_str = str(self.current_user.role.value) if hasattr(self.current_user.role, 'value') else str(self.current_user.role)
            # Manejo enum
            if "Administrador" in role_str:
                show_admin_items = True
                show_manager_items = True
            elif "Gerente" in role_str:
                show_manager_items = True
        
        # Lista de controles
        controls_list = [
            # Logo
            ft.Container(
                padding=ft.padding.only(bottom=20),
                content=ft.Image(
                    src="img/logoNameFlat.png",
                    fit=ft.ImageFit.FIT_WIDTH,
                ),
            ),
            
            # --- Menú Común ---
            # --- Menú Común ---
            self._build_item(ft.Icons.TASK_ALT, "Actividades", is_selected=True),
        ]
        
        # Pendientes (Solo usuarios reales, no perfiles de departamento)
        if isinstance(self.current_user, Usuario):
            controls_list.append(
                self._build_item(ft.Icons.CHECKLIST, "Pendientes")
            )

        # Proyectos
        controls_list.append(
            self._build_item(ft.Icons.ROCKET_LAUNCH_OUTLINED, "Proyectos")
        )
        
        # --- Menú Gerencial/Admin ---

        if show_manager_items:
            controls_list.extend([
                self._build_item(ft.Icons.PEOPLE_OUTLINE, "Usuarios"),
                self._build_item(ft.Icons.CATEGORY_OUTLINED, "Categorias"),
            ])
            
        # --- Menú Admin ---
        if show_admin_items:
            controls_list.extend([
                self._build_item(ft.Icons.BUSINESS, "Departamentos"),
                self._build_item(ft.Icons.VPN_KEY, "Mantenimiento")
            ])

        # Spacer (empujar logout abajo)
        controls_list.append(ft.Container(expand=True))
        
        # --- Info Usuario Logueado ---
        if self.current_user:
            info_content = None
            
            # Caso A: Usuario
            if hasattr(self.current_user, 'role'):
               user_name = f"{self.current_user.nombre} {self.current_user.apellidos}"
               dept_name = self.current_user.departamento.nombre if self.current_user.departamento else "Sin asignar"
               
               info_content = ft.Column(
                   controls=[
                       ft.Text(user_name, weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.WHITE, no_wrap=False, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                       ft.Text(dept_name, size=11, color=ft.Colors.GREY_400, no_wrap=False, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                   ],
                   spacing=0,
                   expand=True
               )
            
            # Caso B: Departamento (Invitado)
            elif hasattr(self.current_user, 'code'):
                dept_name = self.current_user.nombre
                info_content = ft.Column(
                   controls=[
                       ft.Text(dept_name, weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.WHITE, no_wrap=False, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                       ft.Text("Invitado", size=11, color=ft.Colors.GREY_400),
                   ],
                   spacing=0,
                   expand=True
               )

            if info_content:
                controls_list.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.CircleAvatar(
                                    content=ft.Text(user_name[0] if 'user_name' in locals() else dept_name[0], color=ft.Colors.WHITE),
                                    bgcolor=styles.PRIMARY_BLUE,
                                    radius=18
                                ),
                                info_content
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=ft.padding.symmetric(horizontal=10, vertical=10),
                        # bgcolor eliminado para look más limpio
                        border_radius=10
                    )
                )
                controls_list.append(ft.Container(height=5))

        # --- Cerrar Sesión ---
        controls_list.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.EXIT_TO_APP, color=ft.Colors.RED_200, size=20),
                        ft.Text("Cerrar Sesión", color=ft.Colors.RED_200, size=14, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=15,
                    alignment=ft.MainAxisAlignment.CENTER # Centered text/icon looks better on compact buttons
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=10), # Reduced vertical padding
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED), # Transparent Red Background
                border_radius=ft.border_radius.all(10),
                ink=True,
                on_click=lambda e: self.on_logout()
            )
        )

        return ft.Column(
            controls=controls_list,
            spacing=10,
            expand=True # Para que el Column ocupe altura y funcione el spacer
        )