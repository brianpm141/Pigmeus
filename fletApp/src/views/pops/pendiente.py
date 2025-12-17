import flet as ft
import views.styles as styles
from controllers.categorias_controller import get_all_categories
from controllers.pendientes_controller import create_pendiente, update_pendiente
from datetime import datetime
from views.pops.mensaje import Aviso

class PendienteForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, pendiente_data=None, on_success=None, current_user=None):
        super().__init__()
        self.page = page
        self.pendiente_data = pendiente_data
        self.on_success = on_success
        self.current_user = current_user
        
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        # Cargar datos iniciales
        self.categories = get_all_categories(current_user) 
        
        # --- HEADER ---
        title_text = "Modificar Pendiente" if pendiente_data else "Registrar Pendiente"
        self.title = ft.Row([
            ft.Icon(ft.Icons.TASK, color=styles.PRIMARY_BLUE),
            ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR)
        ], alignment=ft.MainAxisAlignment.START)

        # --- CAMPOS ---
        
        # 1. Categoría (Dropdown)
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

        # 2. Descripción
        self.description_field = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error
        )

        # 3. Fecha Prevista (Fecha + Hora)
        self.selected_date = None
        self.selected_time = None
        
        self.date_text = ft.Text("Sin fecha", color=styles.TEXT_COLOR)
        self.time_text = ft.Text("Sin hora", color=styles.TEXT_COLOR)
        
        self.btn_date = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self._open_date_picker,
            tooltip="Seleccionar fecha"
        )
        self.btn_time = ft.IconButton(
            icon=ft.Icons.ACCESS_TIME,
            on_click=self._open_time_picker,
            tooltip="Seleccionar hora"
        )
        
        self.date_picker = ft.DatePicker(
            on_change=self._on_date_change,
        )
        self.time_picker = ft.TimePicker(
            on_change=self._on_time_change,
        )
        
        # 4. Estado
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
        # Default State: Pendiente
        is_completed = False

        # --- PRE-LLENADO (Modificar) ---
        if pendiente_data:
            # Categoría
            cat_id = pendiente_data.get("categoria")
            if cat_id:
                self.category_dropdown.value = str(cat_id)
            
            # Descripción
            self.description_field.value = pendiente_data.get("descripcion", "")
            
            # Fecha y Hora
            dt = pendiente_data.get("fecha_asignada")
            if dt:
                self.selected_date = dt
                self.selected_time = dt.time()
                
                self.date_picker.value = dt
                # self.time_picker.value = dt.time() # Flet timepicker uses value in different format sometimes? uses default value
                
                self.date_text.value = dt.strftime("%d/%m/%Y")
                self.time_text.value = dt.strftime("%H:%M")
            
            # Estado
            is_completed = pendiente_data.get("estado") == "Completada"
            self.status_switch.value = is_completed
        else:
            # Default to today + current time
            self.selected_date = datetime.now()
            self.selected_time = self.selected_date.time()
            
            self.date_text.value = self.selected_date.strftime("%d/%m/%Y")
            self.time_text.value = self.selected_date.strftime("%H:%M")

        self._update_status_visuals(is_completed)

        # --- CONTENIDO ---
        self.content = ft.Container(
            content=ft.Column([
                self.category_dropdown,
                self.description_field,
                ft.Text("Fecha Prevista:", color=styles.TEXT_COLOR, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Icon(ft.Icons.DATE_RANGE, size=16, color=ft.Colors.GREY_500),
                    self.date_text,
                    self.btn_date,
                    ft.Container(width=10),
                    ft.Icon(ft.Icons.ACCESS_TIME, size=16, color=ft.Colors.GREY_500),
                    self.time_text,
                    self.btn_time
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([
                    ft.Text("Estado:", color=styles.TEXT_COLOR), 
                    self.status_switch, 
                    self.status_badge,
                ], alignment=ft.MainAxisAlignment.START, spacing=20),
            ], spacing=15),
            width=450,
            height=450
        )

        # --- BOTONES ---
        self.actions = [
            ft.OutlinedButton("Cancelar", on_click=self.close_dialog),
            ft.ElevatedButton(
                "Guardar" if pendiente_data else "Registrar",
                bgcolor=styles.PRIMARY_BLUE,
                color=ft.Colors.WHITE,
                on_click=self._save_pendiente
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _open_date_picker(self, e):
        self.date_picker.open = True
        self.date_picker.update()

    def _open_time_picker(self, e):
        self.time_picker.open = True
        self.time_picker.update()

    def _on_date_change(self, e):
        if self.date_picker.value:
            self.selected_date = self.date_picker.value
            self.date_text.value = self.selected_date.strftime("%d/%m/%Y")
            if self.date_text.page:
                self.date_text.update()
    
    def _on_time_change(self, e):
        if self.time_picker.value:
            self.selected_time = self.time_picker.value
            self.time_text.value = self.selected_time.strftime("%H:%M")
            if self.time_text.page:
                self.time_text.update()

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

    def _save_pendiente(self, e):
        status_str = "Completada" if self.status_switch.value else "Pendiente"
        
        has_error = False
        
        if not self.category_dropdown.value:
            self.category_dropdown.error_text = "Requerido"
            has_error = True
            
        if not self.description_field.value:
            self.description_field.error_text = "Requerido"
            has_error = True

        if has_error:
            self.page.update()
            return
            
        # Combine Date + Time
        final_datetime = None
        if self.selected_date and self.selected_time:
            final_datetime = datetime.combine(
                self.selected_date.date() if isinstance(self.selected_date, datetime) else self.selected_date, 
                self.selected_time
            )
        elif self.selected_date:
            final_datetime = self.selected_date # Use default time 00:00
            
        # Lógica UPDATE
        if self.pendiente_data:
            res = update_pendiente(
                pendiente_id=self.pendiente_data["id"],
                category_id=int(self.category_dropdown.value),
                description=self.description_field.value,
                fecha_asignada=final_datetime,
                status_str=status_str
            )
        
        # Lógica CREATE
        else:
            if not self.current_user:
                Aviso(self.page, "Error: Usuario no identificado.", is_error=True).show()
                return

            res = create_pendiente(
                user_id=self.current_user.id,
                category_id=int(self.category_dropdown.value),
                description=self.description_field.value,
                fecha_asignada=final_datetime,
                status_str=status_str
            )

        if res["status"] == "success":
            self.close_dialog(None)
            Aviso(self.page, res["message"]).show()
            if self.on_success:
                self.on_success()
        else:
            Aviso(self.page, res["message"], is_error=True).show()

    def open_dialog(self):
        # Attach datepicker/timepicker to overlay if not present
        if self.date_picker not in self.page.overlay:
            self.page.overlay.append(self.date_picker)
        if self.time_picker not in self.page.overlay:
             self.page.overlay.append(self.time_picker)
             
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)
