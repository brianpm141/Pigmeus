import flet as ft
import views.styles as styles
from views.pops.actividad import ActivityForm
from views.pops.actividad_detalles import ActivityDetails
from views.pops.mensaje import Aviso
from views.pops.eliminar import ConfirmationDialog
from views.pops.eliminar import ConfirmationDialog
from controllers.actividades_controller import get_activities, update_activity_status, delete_activity
from controllers.usuarios_controller import get_all_users
from controllers.categorias_controller import get_all_categories

class ActividadesView(ft.Container):
    def _build_filter_menu(self, filter_type, label, current_val, options_list):
        # Encontrar texto a mostrar
        display_text = label
        if str(current_val) != "all":
            # Buscar texto en opciones
            for opt in options_list:
                if str(opt.key) == str(current_val):
                    display_text = opt.text
                    break
        
        # UI del Trigger (Texto + Icono pequeño)
        text_control = ft.Text(
            display_text, 
            size=11, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.GREY_400,
            overflow=ft.TextOverflow.ELLIPSIS, 
            max_lines=1
        )
        
        def on_item_click(e):
            new_val = e.control.data
            
            # Actualizar estado
            if filter_type == "user": self.filter_user_val = new_val
            elif filter_type == "cat": self.filter_cat_val = new_val
            elif filter_type == "status": self.filter_status_val = new_val
            elif filter_type == "start": self.filter_start_val = new_val
            elif filter_type == "end": self.filter_end_val = new_val
            
            self.refresh_data()

        menu_items = []
        for opt in options_list:
            menu_items.append(
                ft.PopupMenuItem(
                    text=opt.text, 
                    data=opt.key, 
                    on_click=on_item_click,
                    checked=(str(current_val) == str(opt.key)) 
                )
            )
            
        return ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row(
                    [
                        text_control,
                        ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=ft.Colors.GREY_400)
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                padding=ft.padding.symmetric(horizontal=0), 
            ),
            items=menu_items,
            tooltip=label
        )

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
        
        # Estados de Filtros de Columna
        self.filter_user_val = "all"
        self.filter_cat_val = "all"
        self.filter_status_val = "all"
        self.filter_start_val = "all"
        self.filter_end_val = "all"
        self.sort_field = "created_at"
        self.sort_desc = True
        
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
        
        # Actualizar ID seleccionado
        if is_selected:
            self.selected_id = act_id
        else:
            if self.selected_id == act_id:
                self.selected_id = None
        
        # Actualizar visualmente la tabla sin reconstruir (mantiene scroll)
        if hasattr(self, 'table') and self.table:
            for row in self.table.rows:

                if row.data == act_id:
                    row.selected = is_selected
                else:
                    if is_selected:
                        row.selected = False
            
            self.table.update()
        
        # NO llamamos refresh_data() completo para evitar scroll jump
        # self.refresh_data()

    def _open_register_modal(self, e):
        form = ActivityForm(e.page, on_success=self.refresh_data, current_user=self.current_user)
        form.open_dialog()

    def _open_modify_modal(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona una actividad para modificar", is_error=True).show()
            return
        self._open_modify_logic(self.selected_id)

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

    def _open_details_modal(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona una actividad para ver detalles.", is_error=True).show()
            return

        # Fetch fresh data
        activities = get_activities()
        selected_act = next((a for a in activities if a.id == self.selected_id), None)
        
        if selected_act:
            details_dialog = ActivityDetails(
                self.page, 
                selected_act, 
                current_user=self.current_user,
                on_edit=lambda id: self._open_modify_from_details(id),
                on_delete=lambda id: self._open_delete_confirmation(id)
            )
            details_dialog.open_dialog()

    def _open_modify_from_details(self, act_id):
        self.selected_id = act_id
        self._open_modify_logic(act_id)

    def _open_delete_confirmation(self, act_id):
        def on_confirm():
            res = delete_activity(act_id)
            if res["status"] == "success":
                self.refresh_data()
                Aviso(self.page, "Actividad eliminada.").show()
            else:
                Aviso(self.page, res["message"], is_error=True).show()
        
        confirm = ConfirmationDialog(self.page, "Eliminar Actividad", "¿Estás seguro de que quieres eliminar esta actividad?", on_confirm)
        confirm.open_dialog()

    def _open_modify_logic(self, act_id):
        activities = get_activities()
        selected_act = next((a for a in activities if a.id == act_id), None)
        
        if selected_act:
            act_data = {
                "id": selected_act.id,
                "usuario_id": selected_act.usuario_id,
                "categoria": selected_act.categoria_id, 
                "detalles": selected_act.descripcion,
                "estado": "Completada" if selected_act.estado == 1 else "Pendiente",
                "colaboradores": [{"id": c.usuario_id, "nombre": f"{c.usuario_rel.nombre} {c.usuario_rel.apellidos}"} for c in selected_act.colaboradores if c.usuario_rel]
            }
            
            form = ActivityForm(self.page, activity_data=act_data, on_success=self.refresh_data, current_user=self.current_user)
            form.open_dialog()

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
            bgcolor=styles.BTN_COMPLETE_BG, # Verde
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
            bgcolor=styles.BTN_MODIFY_BG, # Amarillo
            color=ft.Colors.WHITE,
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
                # Botón Ver Detalles
                ft.ElevatedButton(
                    "Ver Detalles",
                    icon=ft.Icons.VISIBILITY,
                    bgcolor=styles.BTN_PRIMARY_BG, # Azul
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=20, vertical=18)
                    ),
                    on_click=self._open_details_modal
                ),
                self.btn_complete
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.data_container = ft.Container()

    def refresh_data(self):
        dept_filter_val = self.dept_filter.value if self.dept_filter else None
        activities = get_activities(
            self.current_user, 
            filter_dept_id=dept_filter_val,
            filter_user_id=self.filter_user_val,
            filter_category_id=self.filter_cat_val,
            filter_status_int=self.filter_status_val,
            filter_date_start=self.filter_start_val,
            filter_date_end=self.filter_end_val,
            sort_by=self.sort_field,
            sort_desc=self.sort_desc
        )
        
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
        rows_data = []
        # Enforce execution of table creation logic even if no activities found
        if True: 
            for act in activities or []:
                # --- 1. USUARIO ---
                user_nombre = act.usuario_rel.nombre if act.usuario_rel else "Desconocido"
                
                # Limpiar "De [Departamento]" del apellido dinámicamente
                raw_apellido = act.usuario_rel.apellidos if act.usuario_rel else ""
                user_apellido = raw_apellido
                
                # Obtener nombre del depto del usuario
                if act.usuario_rel and act.usuario_rel.departamento:
                    dept_name = act.usuario_rel.departamento.nombre
                    # Construir sufijo a remover: "De Ventas", "De RH"
                    suffix = f"De {dept_name}"
                    user_apellido = user_apellido.replace(suffix, "").strip()

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
                    width=130 # Ancho ajustado para evitar overflow
                )

                # --- 2. CATEGORIA ---
                raw_cat = act.categoria_rel.nombre if act.categoria_rel else "General"
                cat_name = raw_cat
                
                # Limpiar Nombre Depto de la Categoria dinámicamente
                if act.categoria_rel and act.categoria_rel.departamento_rel:
                    cat_dept_name = act.categoria_rel.departamento_rel.nombre
                    # Remover nombre del depto si aparece en la categoria
                    # Ejemplo: "Urgencias Ventas" -> "Urgencias"
                    cat_name = cat_name.replace(cat_dept_name, "").strip()

                cat_cell = ft.Container(
                    content=ft.Text(cat_name, size=14, color=ft.Colors.GREY_700),
                    alignment=ft.alignment.center_left,
                    width=100 # Ancho ajustado
                )

                # --- 3. DETALLES ---
                # Max lines = 2 para evitar que rompa el layout si es muy largo
                detalles_cell = ft.Container(
                    content=ft.Text(act.descripcion, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, size=13, color=ft.Colors.GREY_600),
                    width=180, # Ancho reducido
                    alignment=ft.alignment.center_left 
                )

                # --- 4. ESTADO ---
                estado_cell = ft.Container(
                    content=self._build_status_badge(act.estado),
                    alignment=ft.alignment.center_left,
                    width=100 # Ancho ajustado
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
            
            # -- PREPARAR OPCIONES DE FILTROS --
            # Usuarios (Filtrados por contexto)
            
            is_basic_role = False
            role_str = ""
            if self.current_user and hasattr(self.current_user, 'role'):
                 role_str = str(self.current_user.role.value) if hasattr(self.current_user.role, 'value') else str(self.current_user.role)
                 is_basic_role = "Básico" in role_str
            
            # Determinar Header de Usuario (Texto plano para básico)
            user_header_control = ft.Container(
                ft.Text("USUARIO", color=ft.Colors.GREY_400, size=11, weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center_left,
                padding=ft.padding.only(left=2) # Align with dropdown text
            )
            
            # Solo Admins y Gerentes ven el filtro
            if not is_basic_role:
                users_opts = [ft.dropdown.Option("all", "USUARIO")]
                
                filter_dept_arg = None
                
                # Logic:
                # If Admin -> Use current global dept filter value (self.dept_filter.value)
                if "Administrador" in role_str:
                     # Check global filter
                     if self.dept_filter and self.dept_filter.value != "all":
                         filter_dept_arg = self.dept_filter.value
                
                # If Manager -> Actividades controller already forces them to see only their dept activities.
                # get_all_users should also only return their dept users.
                elif "Gerente" in role_str:
                     filter_dept_arg = self.current_user.departamento_id

                # Determinar si ocultar el sufijo de departamento
                hide_dept_suffix = False
                if "Administrador" not in role_str:
                    # Gerentes/Básicos/Invitados siempre ven solo su depto -> ocultar
                    hide_dept_suffix = True
                else:
                    # Admin: ocultar solo si hay un filtro activo
                    if filter_dept_arg and filter_dept_arg != "all":
                        hide_dept_suffix = True

                relevant_users = get_all_users(dept_id=filter_dept_arg)
                
                for u in relevant_users:
                     # Limpiar nombre base (por si acaso los usuarios tuvieran el depto en el nombre)
                     raw_name = f"{u.nombre} {u.apellidos}"
                     dept_name = u.departamento.nombre if u.departamento else ""
                     
                     clean_name = raw_name
                     if dept_name and dept_name.lower() in raw_name.lower():
                         import re
                         # Remove dept_name from raw_name, case insensitive
                         clean_name = re.sub(re.escape(dept_name), "", raw_name, flags=re.IGNORECASE).strip()
                         # Clean up trailing " de" (case insensitive) -> e.g. "Usuario1 De" -> "Usuario1"
                         clean_name = re.sub(r'\s+de\s*$', '', clean_name, flags=re.IGNORECASE).strip()
                         
                     if hide_dept_suffix:
                         label = clean_name
                     else:
                         if dept_name:
                             label = f"{clean_name} ({dept_name})"
                         else:
                             label = raw_name
                     
                     users_opts.append(ft.dropdown.Option(str(u.id), label))
                
                def on_user_filter_change(e):
                    self.filter_user_val = e.control.value
                    self.refresh_data()

                user_header_control = ft.Container(
                    ft.Dropdown(
                        options=users_opts,
                        value=self.filter_user_val,
                        text_size=11,
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                        content_padding=0,
                        alignment=ft.alignment.center_left,
                        dense=True,
                        border_width=0,
                        hint_text="USUARIO",
                        on_change=on_user_filter_change
                    ),
                    width=85, padding=0
                )

            # Categorias
            cat_opts = [ft.dropdown.Option("all", "CATEGORÍA")]
            
            # Determinar filtro de departamento para categorías
            cat_dept_filter = None
            if self.dept_filter:
                cat_dept_filter = self.dept_filter.value

            relevant_cats = get_all_categories(self.current_user, filter_dept_id=cat_dept_filter) 
            
            # Recalcular flag para categorías (aunque debería ser igual)
            hide_cat_dept_suffix = False
            if "Administrador" not in role_str:
                hide_cat_dept_suffix = True
            else:
                if cat_dept_filter and cat_dept_filter != "all":
                    hide_cat_dept_suffix = True

            for c in relevant_cats:
                raw_name = c.nombre
                dept_name = c.departamento_rel.nombre if c.departamento_rel else ""
                
                # Normalizar nombre: Quitar el nombre del departamento si está incluido en el nombre de la categoría
                # Ejemplo: "General Recursos Humanos" -> "General"
                # Usamos replace insensible a mayúsculas si fuera necesario, pero por ahora simple
                clean_name = raw_name
                if dept_name and dept_name.lower() in raw_name.lower():
                     # Reemplazo simple intentando preservar casing original del resto
                     # Una forma robusta es usar regex re.sub(dept_name, "", raw_name, flags=re.IGNORECASE)
                     import re
                     clean_name = re.sub(re.escape(dept_name), "", raw_name, flags=re.IGNORECASE).strip()
                
                if hide_cat_dept_suffix:
                    # Si estamos filtrados, mostrar solo el nombre limpio
                    label = clean_name
                else:
                    # Si vista general, mostrar formato "Nombre (Depto)"
                    # Si el nombre original YA tenía el depto, clean_name lo quitó, ahora lo ponemos en paréntesis
                    if dept_name:
                        label = f"{clean_name} ({dept_name})"
                    else:
                        label = raw_name

                cat_opts.append(ft.dropdown.Option(str(c.id), label))

            # Status
            status_opts = [
                ft.dropdown.Option("all", "ESTADO"),
                ft.dropdown.Option("0", "Pendientes"),
                ft.dropdown.Option("1", "Completadas"),
            ]

            # Date Filters
            time_opts = [
                ft.dropdown.Option("all", "INICIO / CIERRE"), # Generic default? No, specific per column
            ]
            
            # Start/End need specific defaults because they share list? 
            # No, I should make separate lists or handle it.
            # Let's simple create two lists or just set the label dynamically? 
            # The dropdown uses the list.
            
            start_opts = [
                ft.dropdown.Option("all", "INICIO"),
                ft.dropdown.Option("1h", "Última hora"),
                ft.dropdown.Option("today", "Hoy"),
                ft.dropdown.Option("week", "Esta semana"),
                ft.dropdown.Option("month", "Este mes"),
            ]
            end_opts = [
                ft.dropdown.Option("all", "CIERRE"),
                ft.dropdown.Option("1h", "Última hora"),
                ft.dropdown.Option("today", "Hoy"),
                ft.dropdown.Option("week", "Esta semana"),
                ft.dropdown.Option("month", "Este mes"),
            ]

            # --- HEADER WIDGETS ---
            # Reemplazamos ft.Dropdown con PopupMenuButton usando nuestra función helper
            
            user_header_control = self._build_filter_menu("user", "USUARIO", self.filter_user_val, users_opts)
            
            cat_header = self._build_filter_menu("cat", "CATEGORÍA", self.filter_cat_val, cat_opts)
            
            status_header = self._build_filter_menu("status", "ESTADO", self.filter_status_val, status_opts)
            
            start_header = self._build_filter_menu("start", "INICIO", self.filter_start_val, start_opts)
            
            end_header = self._build_filter_menu("end", "CIERRE", self.filter_end_val, end_opts)
            


            # --- MANEJO DE ESTADO VACÍO ---
            if not rows_data:
                rows_data.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("Sin registros", color=ft.Colors.GREY_400, italic=True)), # Usuario
                            ft.DataCell(ft.Text("")), # Categoria
                            ft.DataCell(ft.Text("")), # Detalles
                            ft.DataCell(ft.Text("")), # Estado
                            ft.DataCell(ft.Text("")), # Inicio
                            ft.DataCell(ft.Text("")), # Cierre
                        ]
                    )
                )

            # Insertar tabla en el card
            self.table = ft.DataTable(
                width=float("inf"),
                heading_row_height=60,
                # CONFIGURACIÓN CLAVE PARA EL ESPACIADO CORRECTO
                data_row_min_height=80,       # Altura mínima reservada
                data_row_max_height=float("inf"), # Crece si es necesario
                column_spacing=5, # Minimal spacing
                divider_thickness=0.5,
                show_checkbox_column=False,
                columns=[
                    ft.DataColumn(
                        ft.Container(user_header_control, width=130, padding=0)
                    ),
                    ft.DataColumn(
                         ft.Container(cat_header, width=100, padding=0),
                    ),
                    ft.DataColumn(
                        ft.Container(
                            ft.Text("DETALLES", color=ft.Colors.GREY_400, size=11, weight=ft.FontWeight.BOLD),
                            width=180 
                        )
                    ),
                    ft.DataColumn(
                         ft.Container(status_header, width=100, padding=0),
                    ),
                    ft.DataColumn(
                        ft.Container(start_header, width=80, padding=0),
                    ),
                    ft.DataColumn(
                        ft.Container(end_header, width=80, padding=0),
                    ),
                ],
                rows=rows_data
            )
            
            # Always show the table (so headers remain visible)
            content_card.content.controls[2] = self.table
            
            # Optional: Add a "No results" message BELOW the table if empty, 
            # but user specifically wants headers.
            # If rows_data is empty, the table will just show headers and no rows.
            

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