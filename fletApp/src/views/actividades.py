import flet as ft
import views.styles as styles
from views.pops.actividad import ActivityForm
from views.pops.mensaje import Aviso
from views.pops.eliminar import ConfirmationDialog
from controllers.actividades_controller import get_activities, update_activity_status, delete_activity

class ActividadesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            controls=self._build_layout(),
        )
        
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
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
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
        form = ActivityForm(e.page, on_success=self.refresh_data)
        form.open_dialog()

    def _open_modify_modal(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona una actividad para modificar", is_error=True).show()
            return
        
        # Buscar actividad en la lista actual (optimización para no ir a BD solo por datos que ya tenemos, 
        # aunque lo ideal es ir a BD. Aquí reusamos lo que tenemos en memoria o hacemos fetch)
        # Haremos fetch fresco mejor.
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
            
            form = ActivityForm(e.page, activity_data=act_data, on_success=self.refresh_data)
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

    # --- UI ---

    def _build_layout(self):
        self.toolbar = ft.Row(
            wrap=True,
            spacing=15,
            controls=[
                ft.ElevatedButton(
                    "Registrar actividad",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    bgcolor=styles.BTN_PRIMARY_BG,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    height=45,
                    on_click=self._open_register_modal
                ),
                ft.ElevatedButton(
                    "Marcar como completado",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    bgcolor=styles.BTN_COMPLETE_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    height=45,
                    on_click=self._mark_completed
                ),
                ft.ElevatedButton(
                    "Modificar",
                    icon=ft.Icons.EDIT_OUTLINED,
                    bgcolor=styles.BTN_MODIFY_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    height=45,
                    on_click=self._open_modify_modal
                ),
            ]
        )
        
        self.data_container = ft.Container()

        return [
            self.toolbar,
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            self.data_container,
            ft.Divider(height=50, color=ft.Colors.TRANSPARENT),
        ]

    def refresh_data(self):
        activities = get_activities()
        
        if activities:
            rows_data = []
            for act in activities:
                # Formatear fechas
                start_date = act.horainicio.strftime("%Y-%m-%d") if act.horainicio else "-"
                start_time = act.horainicio.strftime("%H:%M") if act.horainicio else "-"
                
                end_date = act.horacierre.strftime("%Y-%m-%d") if act.horacierre else "-"
                end_time = act.horacierre.strftime("%H:%M") if act.horacierre else "-"
                
                user_name = f"{act.usuario_rel.nombre} {act.usuario_rel.apellidos}" if act.usuario_rel else "Desconocido"
                cat_name = act.categoria_rel.nombre if act.categoria_rel else "General"
                
                is_selected = (act.id == self.selected_id)

                rows_data.append(
                    ft.DataRow(
                        selected=is_selected,
                        on_select_changed=self._handle_select,
                        data=act.id,
                        cells=[
                            ft.DataCell(ft.Text(user_name, weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(cat_name)),
                            ft.DataCell(ft.Text(act.descripcion, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                            ft.DataCell(self._build_status_badge(act.estado)),
                            ft.DataCell(ft.Text(start_date)),
                            ft.DataCell(ft.Text(start_time)),
                            ft.DataCell(ft.Text(end_date)),
                            ft.DataCell(ft.Text(end_time)),
                        ],
                    )
                )

            self.data_container.content = ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.all(12),
                padding=ft.padding.all(5),
                content=ft.DataTable(
                    width=float("inf"),
                    heading_row_height=60,
                    data_row_min_height=60,
                    column_spacing=20,
                    show_checkbox_column=False,
                    columns=[
                        ft.DataColumn(ft.Text("USUARIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("CATEGORÍA", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("DETALLES", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("ESTADO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("FECHA INICIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("HORA INICIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("FECHA CIERRE", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("HORA CIERRE", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                    ],
                    rows=rows_data
                )
            )
        else:
            self.data_container.content = ft.Container(
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.INBOX_OUTLINED, size=60, color=ft.Colors.GREY_300),
                        ft.Text("No hay actividades registradas.", color=ft.Colors.GREY_500, size=16)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
            )
        if self.page:
            self.update()