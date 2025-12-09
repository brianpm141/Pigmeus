import flet as ft
import views.styles as styles
from views.pops.actividad import ActivityForm
from views.pops.mensaje import Aviso
from views.pops.eliminar import ConfirmationDialog
from controllers.actividades_controller import get_activities, update_activity_status, delete_activity

class ActividadesView(ft.Container):
    def __init__(self, current_user=None):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.current_user = current_user
        
        # Inicializar componentes (toolbar, data_container)
        self._init_layout_components()

        self.content = ft.Column(
            controls=[
                self.header,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.data_container # Contenedor principal variable
            ],
        )
        
        self.data_container.expand = True # Que ocupe todo el espacio restante

        # Estado: ID seleccionado
        self.selected_id = None
        
        # Cargar datos
        self.refresh_data()

    def _build_status_badge(self, status_int):
        # 0 = Pendiente, 1 = Completada
        if status_int == 1:
            text = "Completada"
            bg = styles.STATUS_GREEN_BG
            txt = styles.STATUS_GREEN_TXT
        else:
            text = "Pendiente"
            bg = styles.STATUS_YELLOW_BG
            txt = styles.STATUS_YELLOW_TXT

        return ft.Container(
            content=ft.Text(text, color=txt, size=12, weight=ft.FontWeight.W_500),
            bgcolor=bg,
            width=110,
            height=30,
            padding=ft.padding.symmetric(horizontal=10, vertical=0),
            border_radius=ft.border_radius.all(15),
            alignment=ft.alignment.center
        )

    # --- HANDLERS ---

    def _handle_select(self, e):
        is_selected = e.data == "true"
        act_id = e.control.data 
        
        if is_selected:
            self.selected_id = act_id
        else:
            if self.selected_id == act_id:
                self.selected_id = None
        
        self.refresh_data()

    def _open_register_modal(self, e):
        form = ActivityForm(e.page, on_success=self.refresh_data, current_user=self.current_user)
        form.open_dialog()

    def _open_modify_modal(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona una actividad para modificar", is_error=True).show()
            return
        
        activities = get_activities()
        selected_act = next((a for a in activities if a.id == self.selected_id), None)
        
        if selected_act:
            # Preparar dict para el form
            act_data = {
                "id": selected_act.id,
                "usuario_id": selected_act.usuario_id,
                "categoria": selected_act.categoria_id, 
                "detalles": selected_act.descripcion,
                "estado": "Completada" if selected_act.estado == 1 else "Pendiente"
            }
            
            form = ActivityForm(e.page, activity_data=act_data, on_success=self.refresh_data, current_user=self.current_user)
            form.open_dialog()

    def _mark_completed(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona una actividad.", is_error=True).show()
            return
        
        res = update_activity_status(self.selected_id, "Completada")
        if res["status"] == "success":
            self.refresh_data()
            Aviso(self.page, "Actividad marcada como completada.").show()
        else:
            Aviso(self.page, res["message"], is_error=True).show()

    # --- UI LAYOUT ---

    def _init_layout_components(self):
        # 1. Top Header Area (Page Title + Global Filter)
        
        # Filtro Administrativo (Solo Admins)
        dept_filter_control = ft.Container() # Placeholder vacio por defecto
        self.dept_filter = None
        
        is_admin = False
        if self.current_user and hasattr(self.current_user, 'role'):
            role_str = str(self.current_user.role.value) if hasattr(self.current_user.role, 'value') else str(self.current_user.role)
            if "Administrador" in role_str:
                is_admin = True
        
        if is_admin:
            from controllers.departamentos_controller import get_all_departments
            depts = get_all_departments()
            
            options = [ft.dropdown.Option("all", "Todos los Departamentos")]
            for d in depts:
                options.append(ft.dropdown.Option(str(d.id), d.nombre))
            
            self.dept_filter = ft.Dropdown(
                width=250,
                text_size=14,
                content_padding=10,
                filled=True,
                bgcolor=ft.Colors.GREY_100,
                border_color=ft.Colors.TRANSPARENT,
                border_radius=8,
                value="all",
                options=options,
                on_change=lambda e: self.refresh_data()
            )
            dept_filter_control = self.dept_filter

        self.header = ft.Row(
            controls=[
                ft.Text("Lista de Actividades", size=24, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Container(expand=True),
                dept_filter_control
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # 2. Main Content Card (Table + Actions)
        
        # Botones de Acción
        self.btn_register = ft.ElevatedButton(
            "Registrar",
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            bgcolor=styles.BTN_PRIMARY_BG,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=18)
            ),
            on_click=self._open_register_modal
        )
        
        self.btn_complete = ft.ElevatedButton(
            "Completar",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            bgcolor=styles.BTN_COMPLETE_BG, 
            color=styles.BTN_TEXT_WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=18)
            ),
            on_click=self._mark_completed
        )
        
        # Barra de Título de Tabla + Botones
        self.action_bar = ft.Row(
            controls=[
                ft.Text("Registro de Actividades", size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Container(expand=True),
                self.btn_register,
                self.btn_complete
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.data_container = ft.Container()

    def refresh_data(self):
        dept_filter_val = self.dept_filter.value if self.dept_filter else None
        activities = get_activities(self.current_user, filter_dept_id=dept_filter_val)
        
        # Reconstruir el contenido principal cada vez
        content_card = ft.Container(
            content=ft.Column(
                controls=[
                    self.action_bar,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Container() # Placeholder
                ],
                spacing=0
            ),
            bgcolor=ft.Colors.WHITE,
            padding=30,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        )

        if activities:
            rows_data = []
            for act in activities:
                # --- 1. USUARIO ---
                user_nombre = act.usuario_rel.nombre if act.usuario_rel else "Desconocido"
                
                # Limpiar "De [Departamento]" del apellido
                raw_apellido = act.usuario_rel.apellidos if act.usuario_rel else ""
                user_apellido = raw_apellido
                for d_name in ["De Ventas", "De RH", "De Desarrollo"]:
                    user_apellido = user_apellido.replace(d_name, "").strip()
                
                user_column = ft.Column(
                    controls=[
                        ft.Text(user_nombre, weight=ft.FontWeight.BOLD, size=14, color=styles.TEXT_COLOR),
                        ft.Text(user_apellido, size=12, color=ft.Colors.GREY_600)
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER 
                )
                
                # Container FLUIDO (sin height fijo), con padding vertical
                user_cell = ft.Container(
                    content=user_column,
                    alignment=ft.alignment.center_left,
                    padding=ft.padding.symmetric(vertical=10),
                    width=160 # Ancho fijo estandarizado
                )

                # --- 2. CATEGORIA ---
                raw_cat = act.categoria_rel.nombre if act.categoria_rel else "General"
                cat_name = raw_cat
                for badge in [" Ventas", " RH", " Desarrollo"]:
                    cat_name = cat_name.replace(badge, "").strip()

                cat_cell = ft.Container(
                    content=ft.Text(cat_name, size=14, color=ft.Colors.GREY_700),
                    alignment=ft.alignment.center_left,
                    width=120 # Ancho fijo estandarizado
                )

                # --- 3. DETALLES ---
                # Max lines = 2 para evitar que rompa el layout si es muy largo
                detalles_cell = ft.Container(
                    content=ft.Text(act.descripcion, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, size=13, color=ft.Colors.GREY_600),
                    width=220, # Ancho fijo (ya estaba)
                    alignment=ft.alignment.center_left 
                )

                # --- 4. ESTADO ---
                estado_cell = ft.Container(
                    content=self._build_status_badge(act.estado),
                    alignment=ft.alignment.center_left,
                    width=120 # Ancho fijo estandarizado
                )

                # --- 5. FECHAS (Hora / Fecha) ---
                def format_date_cell(dt):
                    if not dt: return ft.Container(content=ft.Text("-"), alignment=ft.alignment.center, width=80)
                    time_str = dt.strftime("%H:%M")
                    date_str = dt.strftime("%d/%m")
                    col = ft.Column(
                        controls=[
                            ft.Text(time_str, weight=ft.FontWeight.BOLD, size=14, color=styles.TEXT_COLOR),
                            ft.Text(date_str, size=12, color=ft.Colors.GREY_500)
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                    return ft.Container(content=col, alignment=ft.alignment.center, width=80) # Ancho fijo

                start_cell = format_date_cell(act.horainicio)
                end_cell = format_date_cell(act.horacierre)
                
                is_selected = (act.id == self.selected_id)

                rows_data.append(
                    ft.DataRow(
                        selected=is_selected,
                        on_select_changed=self._handle_select,
                        data=act.id,
                        cells=[
                            ft.DataCell(user_cell),
                            ft.DataCell(cat_cell),
                            ft.DataCell(detalles_cell),
                            ft.DataCell(estado_cell),
                            ft.DataCell(start_cell),
                            ft.DataCell(end_cell),
                        ],
                    )
                )
            
            # Insertar tabla en el card
            content_card.content.controls[2] = ft.DataTable(
                width=float("inf"),
                heading_row_height=60,
                # CONFIGURACIÓN CLAVE PARA EL ESPACIADO CORRECTO
                data_row_min_height=80,       # Altura mínima reservada
                data_row_max_height=float("inf"), # Crece si es necesario
                column_spacing=20,
                divider_thickness=0.5,
                show_checkbox_column=False,
                columns=[
                    ft.DataColumn(ft.Text("USUARIO", color=ft.Colors.GREY_400, size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("CATEGORÍA", color=ft.Colors.GREY_400, size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("DETALLES", color=ft.Colors.GREY_400, size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("ESTADO", color=ft.Colors.GREY_400, size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("INICIO", color=ft.Colors.GREY_400, size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("CIERRE", color=ft.Colors.GREY_400, size=12, weight=ft.FontWeight.BOLD)),
                ],
                rows=rows_data
            )
        else:
            # Empty State
            content_card.content.controls[2] = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.INBOX_OUTLINED, size=50, color=ft.Colors.GREY_300),
                        ft.Text("No hay actividades registradas.", color=ft.Colors.GREY_400, size=14)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                padding=50,
                alignment=ft.alignment.center
            )

        # Actualizar el contenedor principal
        self.data_container.content = ft.Column(
             controls=[
                 ft.Container(height=10),
                 content_card
             ],
             scroll=ft.ScrollMode.AUTO
        )
        
        if self.page:
            self.update()