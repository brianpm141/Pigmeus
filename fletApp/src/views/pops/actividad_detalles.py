
import flet as ft
import views.styles as styles

class ActivityDetails(ft.AlertDialog):
    def __init__(self, page: ft.Page, activity_obj, current_user=None, on_edit=None, on_delete=None):
        super().__init__()
        self.page = page
        self.activity = activity_obj
        self.current_user = current_user
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=12)
        
        self._build_content()
        self._build_actions()

    # ... (existing _build_content) ...

    def _check_permissions(self):
        if not self.current_user:
            return False
            
        # Role string safely
        role_str = str(self.current_user.role.value) if hasattr(self.current_user, 'role') and hasattr(self.current_user.role, 'value') else str(getattr(self.current_user, 'role', ''))
        
        # 1. Dueño
        if self.current_user.id == self.activity.usuario_id:
            return True
            
        # 2. Admin
        if "Administrador" in role_str:
            return True
            
        # 3. Gerente de Mismo Depto
        if "Gerente" in role_str:
            # Check departments
            user_dept_id = getattr(self.current_user, 'departamento_id', None)
            act_dept_id = self.activity.usuario_rel.departamento_id if self.activity.usuario_rel else None
            
            if user_dept_id and act_dept_id and user_dept_id == act_dept_id:
                return True
                
        return False

    def _build_actions(self):
        can_modify = self._check_permissions()
        
        self.actions = [ft.TextButton("Cerrar", on_click=self.close_dialog)]
        
        if can_modify:
            self.actions.append(ft.Container(width=10))
            self.actions.append(ft.OutlinedButton("Eliminar", icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, on_click=self._handle_delete, style=ft.ButtonStyle(color=ft.Colors.RED_400)))
            self.actions.append(ft.ElevatedButton("Modificar", icon=ft.Icons.EDIT, bgcolor=styles.PRIMARY_BLUE, color=ft.Colors.WHITE, on_click=self._handle_edit))
            
        self.actions_alignment = ft.MainAxisAlignment.END

    def _build_content(self):
        # Datos del objeto
        user_name = self.activity.usuario_rel.nombre if self.activity.usuario_rel else "Desconocido"
        user_lastname = self.activity.usuario_rel.apellidos if self.activity.usuario_rel else ""
        if self.activity.usuario_rel and self.activity.usuario_rel.departamento:
             suffix = f"De {self.activity.usuario_rel.departamento.nombre}"
             user_lastname = user_lastname.replace(suffix, "").strip()
        
        full_name = f"{user_name} {user_lastname}"
        dept_name = self.activity.usuario_rel.departamento.nombre if (self.activity.usuario_rel and self.activity.usuario_rel.departamento) else "Sin Depto"
        
        category = self.activity.categoria_rel.nombre if self.activity.categoria_rel else "General"
        
        status_text = "Completada" if self.activity.estado == 1 else "Pendiente"
        status_color = styles.STATUS_GREEN_TXT if self.activity.estado == 1 else styles.STATUS_YELLOW_TXT
        status_bg = styles.STATUS_GREEN_BG if self.activity.estado == 1 else styles.STATUS_YELLOW_BG
        
        details = self.activity.descripcion
        
        # Colaboradores
        collabs = []
        if self.activity.colaboradores:
            for c in self.activity.colaboradores:
                if c.usuario_rel:
                     c_name = f"{c.usuario_rel.nombre} {c.usuario_rel.apellidos}"
                     # Limpieza apellidos (opcional, pero consistente)
                     c_dept = c.usuario_rel.departamento.nombre if c.usuario_rel.departamento else ""
                     if c_dept: c_name = c_name.replace(f"De {c_dept}", "").strip()
                     collabs.append(c_name)
        
        # UI Components
        
        def label_value(label, value, icon=None):
            return ft.Column([
                ft.Row([
                    ft.Icon(icon, size=16, color=styles.PRIMARY_BLUE) if icon else ft.Container(),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD),
                ], spacing=5),
                ft.Text(value, size=14, color=styles.TEXT_COLOR, selectable=True)
            ], spacing=2)

        self.title = ft.Row(
            [ft.Icon(ft.Icons.VISIBILITY, color=styles.PRIMARY_BLUE), ft.Text("Detalles de Actividad", weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.START
        )
        
        collab_control = ft.Container()
        if collabs:
            collab_list = ft.Column(spacing=2)
            for c in collabs:
                collab_list.controls.append(ft.Row([ft.Icon(ft.Icons.PERSON_OUTLINE, size=14, color=ft.Colors.GREY_500), ft.Text(c, size=13)]))
            
            collab_control = ft.Column([
                ft.Divider(color=ft.Colors.TRANSPARENT, height=10),
                ft.Text("Equipo:", size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD),
                ft.Container(collab_list, bgcolor=ft.Colors.GREY_50, padding=10, border_radius=8)
            ])

        self.content = ft.Container(
            width=500,
            content=ft.Column([
                ft.Row([
                    ft.Column([
                         label_value("Usuario", full_name, ft.Icons.PERSON),
                         ft.Container(height=10),
                         label_value("Departamento", dept_name, ft.Icons.BUSINESS),
                    ], expand=True),
                    
                    ft.Column([
                         label_value("Categoría", category, ft.Icons.CATEGORY),
                         ft.Container(height=10),
                         ft.Column([
                             ft.Text("Estado", size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD),
                             ft.Container(
                                 content=ft.Text(status_text, color=status_color, size=12, weight=ft.FontWeight.BOLD),
                                 bgcolor=status_bg,
                                 padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                 border_radius=15
                             )
                         ])
                    ], expand=True),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(color=ft.Colors.GREY_200),
                
                label_value("Detalles", details, ft.Icons.DESCRIPTION),
                
                collab_control,

            ], scroll=ft.ScrollMode.AUTO)
        )
        


    def _handle_edit(self, e):
        self.close_dialog(None)
        if self.on_edit:
            self.on_edit(self.activity.id)

    def _handle_delete(self, e):
        self.close_dialog(None)
        if self.on_delete:
            self.on_delete(self.activity.id)

    def open_dialog(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)
