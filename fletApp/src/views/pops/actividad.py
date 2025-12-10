import flet as ft
import views.styles as styles
from controllers.usuarios_controller import get_all_users
from controllers.actividades_controller import create_activity, update_activity
from controllers.categorias_controller import get_all_categories
from controllers.departamentos_controller import get_all_departments
from views.pops.mensaje import Aviso

class ActivityForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, activity_data=None, on_success=None, current_user=None):
        super().__init__()
        self.page = page
        self.activity_data = activity_data
        self.on_success = on_success
        self.current_user = current_user
        
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        # Estado Local
        self.selected_collabs = [] # Lista de dicts: {id, nombre}
        
        # Cargar datos iniciales
        self.users = get_all_users(current_user)
        self.categories = get_all_categories(current_user) 
        self.departments = get_all_departments() # Para seleccionar colaboradores de otros deptos

        # --- HEADER ---
        title_text = "Modificar Actividad" if activity_data else "Registrar Actividad"
        self.title = ft.Row([
            ft.Icon(ft.Icons.ASSIGNMENT, color=styles.PRIMARY_BLUE),
            ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR)
        ], alignment=ft.MainAxisAlignment.START)

        # --- CAMPOS PRINCIPALES ---
        
        # 1. Usuario (Dueño) Dropdown
        self.user_dropdown = ft.Dropdown(
            label="Usuario",
            width=400,
            options=[ft.dropdown.Option(key=str(u.id), text=f"{u.nombre} {u.apellidos}") for u in self.users],
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._on_user_change
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

        # 6. Texto de Advertencia (Inline)
        self.warning_text = ft.Text(size=12, visible=False, text_align=ft.TextAlign.CENTER)

        # --- SECCIÓN COLABORADORES ---
        
        # --- SECCIÓN COLABORADORES (Componentes) ---
        
        # --- SECCIÓN COLABORADORES (Componentes) ---
        
        self.btn_add_collab = ft.TextButton(
            "Añadir Colaborador",
            icon=ft.Icons.PERSON_ADD,
            style=ft.ButtonStyle(
                color=styles.PRIMARY_BLUE,
                padding=ft.padding.all(0),
            ),
            on_click=self._toggle_collab_ui
        )
        
        # UI de Selección (Oculta por defecto)
        self.collab_dept_dropdown = ft.Dropdown(
            label="Departamento",
            width=180,
            options=[ft.dropdown.Option(key=str(d.id), text=d.nombre) for d in self.departments],
            text_size=12,
            content_padding=5,
            filled=True,
            on_change=self._on_collab_dept_change
        )
        
        self.collab_user_dropdown = ft.Dropdown(
            label="Colaborador",
            width=180,
            options=[],
            text_size=12,
            content_padding=5,
            filled=True,
            disabled=True
        )
        
        self.btn_confirm_collab = ft.IconButton(
            icon=ft.Icons.CHECK_CIRCLE,
            icon_color=ft.Colors.GREEN,
            tooltip="Confirmar",
            on_click=self._confirm_add_collab
        )
        
        self.collab_selection_row = ft.Row(
            [
                ft.Column([self.collab_dept_dropdown, self.collab_user_dropdown], spacing=5),
                self.btn_confirm_collab
            ],
            # visible=False, # Ya no ocultamos esto internamente, sino toda la columna
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.END
        )
        
        # Lista visual de colaboradores
        self.collab_list_view = ft.Column(spacing=5)
        
        # --- PRE-CONFIGURACIÓN (Auth Automática) ---
        self.is_authenticated_user = False
        if self.current_user and hasattr(self.current_user, 'role'):
            self.is_authenticated_user = True
            
            # Pre-seleccionar usuario
            self.user_dropdown.value = str(self.current_user.id)
            self.user_dropdown.visible = False
            self.password_field.visible = False

        # --- PRE-LLENADO (Modificar) ---
        if activity_data:
            # Usuario
            user_id = activity_data.get("usuario_id")
            if user_id:
                self.user_dropdown.value = str(user_id)
                self.user_dropdown.disabled = True 
                self.user_dropdown.visible = True 
                self.password_field.visible = False
            
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
            
            # Cargar colaboradores existentes
            if "colaboradores" in activity_data:
                for col in activity_data["colaboradores"]:
                    self.selected_collabs.append(col)
                self._refresh_collab_list()

        
        # --- LAYOUT (2 COLUMNAS) ---
        
        # Columna Izquierda: Datos Principales
        left_controls = [
            self.user_dropdown,
            self.password_field if not activity_data else ft.Container(),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.category_dropdown,
            self.details_field,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.warning_text, # Added warning text here
            ft.Row([
                ft.Text("Estado:", color=styles.TEXT_COLOR), 
                self.status_switch, 
                self.status_badge,
                ft.Container(expand=True), # Spacer
                self.btn_add_collab 
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
        ]

        # Columna Derecha: Colaboradores
        self.right_column_content = ft.Column(
            [
                ft.Text("Equipo:", size=14, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.collab_selection_row,
                ft.Container(height=10),
                self.collab_list_view 
            ],
            width=250, 
            scroll=ft.ScrollMode.AUTO,
            visible=False # Inicialmente oculto
        )
        
        self.vertical_divider = ft.VerticalDivider(width=30, color=ft.Colors.GREY_200, visible=False)

        self.content_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(left_controls, expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    self.vertical_divider,
                    self.right_column_content
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            width=500, # Initial small width
            height=500,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT) # Animación de resize suave
        )
        
        self.content = self.content_container

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
    
    # --- METODOS UI ---

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

    # --- LOGICA COLABORADORES ---
    
    def _toggle_collab_ui(self, e):
        # Validar antes de abrir
        if not self.is_authenticated_user and not self.user_dropdown.value:
             self._show_warning("Debe seleccionar un usuario antes de añadir colaboradores.", is_error=True)
             return

        # Toggle visibilidad de la sección derecha
        is_visible = not self.right_column_content.visible
        
        self.right_column_content.visible = is_visible
        self.vertical_divider.visible = is_visible
        
        # Ajustar ancho del diálogo
        if is_visible:
            self.content_container.width = 800
        else:
            self.content_container.width = 500
            
        self.content_container.update()
        # Nota: En AlertDialog el update parcial a veces es tricky, pero content.update() suele funcionar si content es Container
        # Si no, self.page.update()
        # self.page.update() # Refuerzo por si acaso
        
    def _on_collab_dept_change(self, e):
        dept_id = self.collab_dept_dropdown.value
        if not dept_id: return
        
        # Cargar usuarios de ese depto
        users_dept = get_all_users(self.current_user, filter_dept_id=int(dept_id))
        
        self.collab_user_dropdown.options = [
            ft.dropdown.Option(key=str(u.id), text=f"{u.nombre} {u.apellidos}") 
            for u in users_dept
        ]
        self.collab_user_dropdown.value = None
        self.collab_user_dropdown.disabled = False
        self.collab_user_dropdown.update()

    def _on_user_change(self, e):
        self._clear_error(e)
        self._clear_warning()
        
        # Verificar conflicto con colaboradores
        new_user_id = int(self.user_dropdown.value) if self.user_dropdown.value else None
        if not new_user_id: return
        
        # Buscar si este usuario está en colaboradores
        collab_found = None
        for c in self.selected_collabs:
            if c["id"] == new_user_id:
                collab_found = c["id"]
                break
        
        if collab_found:
            self._remove_collab(collab_found)
            self._show_warning("El usuario seleccionado estaba como colaborador y ha sido eliminado de la lista.", is_error=False)

    def _confirm_add_collab(self, e):
        # Validar selección de usuario principal (si no es auth)
        if not self.is_authenticated_user and not self.user_dropdown.value:
             self._show_warning("Debe seleccionar un usuario principal antes de añadir colaboradores.", is_error=True)
             return

        user_id = self.collab_user_dropdown.value
        if not user_id: return
        
        # Validar duplicados
        if any(str(c['id']) == user_id for c in self.selected_collabs):
            # Ya existe
            return
            
        # Verificar que no sea el mismo dueño
        current_owner_id = self.user_dropdown.value
        if current_owner_id and str(current_owner_id) == user_id:
             self._show_warning("No puede añadirse a sí mismo como colaborador.", is_error=True)
             return

        # Obtener texto del usuario
        user_text = ""
        for opt in self.collab_user_dropdown.options:
            if opt.key == user_id:
                user_text = opt.text
                break
        
        self.selected_collabs.append({"id": int(user_id), "nombre": user_text})
        self._refresh_collab_list()
        
        # Reset UI parcial
        self.collab_user_dropdown.value = None
        self.collab_user_dropdown.update()

    def _show_warning(self, message, is_error=True):
        self.warning_text.value = message
        self.warning_text.color = ft.Colors.RED_400 if is_error else ft.Colors.ORANGE_400
        self.warning_text.visible = True
        self.warning_text.update()
        
    def _clear_warning(self):
        if self.warning_text.visible:
            self.warning_text.visible = False
            self.warning_text.value = ""
            self.warning_text.update()
        
    def _refresh_collab_list(self):
        self.collab_list_view.controls.clear()
        
        for collab in self.selected_collabs:
            row = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.GREY_600),
                    ft.Text(collab["nombre"], size=14, color=styles.TEXT_COLOR, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE, 
                        icon_size=16, 
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, cid=collab["id"]: self._remove_collab(cid)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.Colors.GREY_50,
                border_radius=5,
                padding=5,
                border=ft.border.all(1, ft.Colors.GREY_200)
            )
            self.collab_list_view.controls.append(row)
        
        self.collab_list_view.update()

    def _remove_collab(self, collab_id):
        self.selected_collabs = [c for c in self.selected_collabs if c["id"] != collab_id]
        self._refresh_collab_list()

    # --- GUARDAR ---

    def _save_activity(self, e):
        status_str = "Completada" if self.status_switch.value else "Pendiente"
        
        has_error = False
        
        # Validaciones comunes
        if not self.category_dropdown.value:
            self.category_dropdown.error_text = "Requerido"
            has_error = True

        # Preparamos lista de IDs
        collab_ids = [c["id"] for c in self.selected_collabs]

        # Lógica UPDATE
        if self.activity_data:
            if has_error:
                self.page.update()
                return
            
            res = update_activity(
                activity_id=self.activity_data["id"],
                category_id=int(self.category_dropdown.value),
                details=self.details_field.value,
                status_str=status_str,
                collaborator_ids=collab_ids
            )
        
        # Lógica CREATE
        else:
            if not self.user_dropdown.value:
                self.user_dropdown.error_text = "Requerido"
                has_error = True
            
            # Solo validar contraseña si NO es usuario autenticado
            password_val = ""
            skip_pass = False
            
            if self.is_authenticated_user:
                skip_pass = True
            else:
                if not self.password_field.value:
                    self.password_field.error_text = "Requerida"
                    has_error = True
                password_val = self.password_field.value
                
            if has_error:
                self.page.update()
                return

            res = create_activity(
                user_id=int(self.user_dropdown.value),
                password_attempt=password_val,
                category_id=int(self.category_dropdown.value),
                details=self.details_field.value,
                status_str=status_str,
                collaborator_ids=collab_ids,
                skip_password_check=skip_pass
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