import flet as ft
import views.styles as styles
from views.pops.pendiente import PendienteForm
from views.pops.mensaje import Aviso
from views.pops.eliminar import ConfirmationDialog
from controllers.pendientes_controller import get_pendientes, update_pendiente_status, delete_pendiente
from controllers.categorias_controller import get_all_categories

class PendingView(ft.Container):
    def _build_filter_menu(self, filter_type, label, current_val, options_list):
        display_text = label
        if str(current_val) != "all":
            for opt in options_list:
                if str(opt.key) == str(current_val):
                    display_text = opt.text
                    break
        
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
            
            if filter_type == "cat": self.filter_cat_val = new_val
            elif filter_type == "status": self.filter_status_val = new_val
            
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
        
        # Filtros
        self.filter_cat_val = "all"
        self.filter_status_val = "all"
        self.sort_field = "created_at"
        self.sort_desc = True
        self.selected_id = None

        # UI Components
        self._init_layout_components()

        self.content = ft.Column(
            controls=[
                self.header,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.data_container
            ],
        )
        self.data_container.expand = True
        
        self.refresh_data()

    def _build_status_badge(self, status_int):
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
        p_id = e.control.data 
        
        if is_selected:
            self.selected_id = p_id
        else:
            if self.selected_id == p_id:
                self.selected_id = None
        
        if hasattr(self, 'table') and self.table:
            for row in self.table.rows:
                if row.data == p_id:
                    row.selected = is_selected
                else:
                    if is_selected:
                        row.selected = False
            self.table.update()

    def _open_register_modal(self, e):
        form = PendienteForm(self.page, on_success=self.refresh_data, current_user=self.current_user)
        form.open_dialog()

    def _open_modify_modal(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona un pendiente para modificar", is_error=True).show()
            return

        pendientes = get_pendientes(self.current_user) # Idealmente cachear esto o fetch simple
        selected_p = next((p for p in pendientes if p.id == self.selected_id), None)
        
        if selected_p:
            p_data = {
                "id": selected_p.id,
                "categoria": selected_p.categoria_id,
                "descripcion": selected_p.descripcion,
                "fecha_asignada": selected_p.fecha_asignada,
                "estado": "Completada" if selected_p.estado == 1 else "Pendiente"
            }
            form = PendienteForm(self.page, pendiente_data=p_data, on_success=self.refresh_data, current_user=self.current_user)
            form.open_dialog()

    def _open_delete_confirmation(self, e):
        if not self.selected_id:
             Aviso(self.page, "Selecciona un pendiente para eliminar", is_error=True).show()
             return

        def on_confirm():
            res = delete_pendiente(self.selected_id)
            if res["status"] == "success":
                self.refresh_data()
                self.selected_id = None
                Aviso(self.page, "Pendiente eliminado.").show()
            else:
                Aviso(self.page, res["message"], is_error=True).show()
        
        confirm = ConfirmationDialog(self.page, "Eliminar Pendiente", "¿Estás seguro de que quieres eliminar este pendiente?", on_confirm)
        confirm.open_dialog()

    def _mark_completed(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona un pendiente.", is_error=True).show()
            return
        
        res = update_pendiente_status(self.selected_id, "Completada")
        if res["status"] == "success":
            self.refresh_data()
            Aviso(self.page, "Marcado como completado.").show()
        else:
            Aviso(self.page, res["message"], is_error=True).show()

    # --- UI LAYOUT ---

    def _init_layout_components(self):
        self.header = ft.Row(
            controls=[
                ft.Text("Mis Pendientes", size=24, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Container(expand=True),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Botones
        self.btn_register = ft.ElevatedButton(
            "Registrar",
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            bgcolor=styles.BTN_COMPLETE_BG, 
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=18)
            ),
            on_click=self._open_register_modal
        )

        self.btn_modify = ft.ElevatedButton(
            "Modificar",
            icon=ft.Icons.EDIT,
            bgcolor=styles.BTN_PRIMARY_BG,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=18)
            ),
            on_click=self._open_modify_modal
        )
        
        self.btn_delete = ft.ElevatedButton(
            "Eliminar",
            icon=ft.Icons.DELETE_OUTLINE,
            bgcolor=ft.Colors.RED_400,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=18)
            ),
            on_click=self._open_delete_confirmation
        )

        self.btn_complete = ft.ElevatedButton(
            "Completar",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            bgcolor=styles.BTN_MODIFY_BG, 
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=18)
            ),
            on_click=self._mark_completed
        )

        self.action_bar = ft.Row(
            controls=[
                ft.Text("Listado", size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Container(expand=True),
                self.btn_register,
                self.btn_modify,
                self.btn_delete,
                self.btn_complete
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.data_container = ft.Container()

    def refresh_data(self):
        pendientes = get_pendientes(
            self.current_user,
            filter_category_id=self.filter_cat_val,
            filter_status_int=self.filter_status_val,
            sort_by=self.sort_field,
            sort_desc=self.sort_desc
        )

        content_card = ft.Container(
            content=ft.Column(
                controls=[
                    self.action_bar,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Container() # Placeholder tabla
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
        for p in pendientes or []:
            # 1. Categoria
            cat_name = p.categoria_rel.nombre if p.categoria_rel else "General"
            cat_cell = ft.Container(
                content=ft.Text(cat_name, size=14, color=ft.Colors.GREY_700),
                alignment=ft.alignment.center_left,
                width=150
            )

            # 2. Descripción
            desc_cell = ft.Container(
                content=ft.Text(p.descripcion, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, size=13, color=ft.Colors.GREY_600),
                width=250,
                alignment=ft.alignment.center_left 
            )

            # 3. Fecha Prevista
            fecha_str = "-"
            time_str = ""
            if p.fecha_asignada:
                # Format: DD/MM/YY HH:MM
                fecha_str = p.fecha_asignada.strftime("%d/%m")
                time_str = p.fecha_asignada.strftime("%H:%M")
            
            date_col = ft.Column(
                controls=[
                    ft.Text(time_str, weight=ft.FontWeight.BOLD, size=14, color=styles.TEXT_COLOR),
                    ft.Text(fecha_str, size=12, color=ft.Colors.GREY_500)
                ],
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER
            )
            
            date_cell = ft.Container(
                content=date_col,
                width=100,
                alignment=ft.alignment.center_left
            )

            # 4. Estado
            estado_cell = ft.Container(
                content=self._build_status_badge(p.estado),
                alignment=ft.alignment.center_left,
                width=100
            )

            is_selected = (p.id == self.selected_id)

            rows_data.append(
                ft.DataRow(
                    selected=is_selected,
                    on_select_changed=self._handle_select,
                    data=p.id,
                    cells=[
                        ft.DataCell(cat_cell),
                        ft.DataCell(desc_cell),
                        ft.DataCell(date_cell),
                        ft.DataCell(estado_cell),
                    ],
                )
            )

        # Filters
        cat_opts = [ft.dropdown.Option("all", "CATEGORÍA")]
        # Cargar categorias disponibles
        all_cats = get_all_categories(self.current_user)
        for c in all_cats:
            cat_opts.append(ft.dropdown.Option(str(c.id), c.nombre))

        status_opts = [
            ft.dropdown.Option("all", "ESTADO"),
            ft.dropdown.Option("0", "Pendientes"),
            ft.dropdown.Option("1", "Completadas"),
        ]

        cat_header = self._build_filter_menu("cat", "CATEGORÍA", self.filter_cat_val, cat_opts)
        status_header = self._build_filter_menu("status", "ESTADO", self.filter_status_val, status_opts)

        if not rows_data:
            rows_data.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Sin pendientes", color=ft.Colors.GREY_400, italic=True)), 
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ]
                )
            )

        self.table = ft.DataTable(
            width=float("inf"),
            heading_row_height=60,
            data_row_min_height=80,
            column_spacing=10,
            divider_thickness=0.5,
            show_checkbox_column=False,
            columns=[
                ft.DataColumn(ft.Container(cat_header, width=150, padding=0)),
                ft.DataColumn(ft.Container(ft.Text("DESCRIPCIÓN", color=ft.Colors.GREY_400, size=11, weight=ft.FontWeight.BOLD), width=250)),
                ft.DataColumn(ft.Container(ft.Text("FECHA PREVISTA", color=ft.Colors.GREY_400, size=11, weight=ft.FontWeight.BOLD), width=100)),
                ft.DataColumn(ft.Container(status_header, width=100, padding=0)),
            ],
            rows=rows_data
        )

        content_card.content.controls[2] = self.table

        self.data_container.content = ft.Column(
             controls=[
                 ft.Container(height=10),
                 content_card
             ],
             scroll=ft.ScrollMode.AUTO
        )
        
        if self.page:
            self.update()
