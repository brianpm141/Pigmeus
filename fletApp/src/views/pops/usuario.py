import flet as ft
import views.styles as styles
import controllers.usuarios_controller as controller # Asegurate que este nombre sea correcto (user_controller o usuarios_controller)
import controllers.departamentos_controller as dept_controller
from views.pops.mensaje import Aviso

class UserForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, user_data=None, on_success=None):
        super().__init__()
        self.page = page
        self.user_data = user_data
        self.on_success = on_success
        
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=12)
        
        # --- Textos ---
        title_text = "Modificar Usuario" if user_data else "Registrar Usuario"
        sub_title = "Gestione los datos de acceso y perfil."
        
        self.title = ft.Column(
            [
                ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Text(sub_title, size=12, color=ft.Colors.GREY_500),
            ],
            spacing=5
        )

        # ==================== DEFINICIÓN DE CAMPOS ====================

        # --- Credenciales ---
        self.username_field = ft.TextField(
            label="Usuario (Login)",
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            expand=True,
            on_change=self._clear_error
        )

        self.password_field = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            expand=True,
            on_change=self._clear_error
        )

        self.confirm_pass_field = ft.TextField(
            label="Confirmar Contraseña",
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            prefix_icon=ft.Icons.LOCK_RESET,
            expand=True,
            on_change=self._clear_error
        )

        # --- Datos Personales ---
        self.name_field = ft.TextField(
            label="Nombre(s)", border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR), label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            expand=True,
            on_change=self._clear_error
        )

        self.lastname_field = ft.TextField(
            label="Apellidos", border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR), label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            expand=True,
            on_change=self._clear_error
        )

        self.id_field = ft.TextField(
            label="Matrícula / ID", border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR), label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            expand=True,
            on_change=self._clear_error
        )

        self.dept_dropdown = ft.Dropdown(
            label="Departamento", border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR), label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            expand=True,
            on_change=self._clear_error
        )
        
        self.role_dropdown = ft.Dropdown(
            label="Rol / Permisos", border_color=ft.Colors.GREY_300,
            options=[
                ft.dropdown.Option("Básico"),
                ft.dropdown.Option("Gerente"),
                ft.dropdown.Option("Administrador"),
            ],
            text_style=ft.TextStyle(color=styles.TEXT_COLOR), label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            value="Básico",
            expand=True,
            on_change=self._clear_error
        )

        # Cargar departamentos desde la BD
        self._load_departments()

        # ==================== LOGICA DE EDICIÓN ====================
        # Si estamos editando, ocultamos password y llenamos datos
        password_section = ft.Container() # Vacio por defecto

        if user_data:
            # -- MODO EDICIÓN --
            self.username_field.value = user_data.get("user")
            self.username_field.disabled = True # No se puede cambiar el usuario
            self.name_field.value = user_data.get("nombre")
            self.lastname_field.value = user_data.get("apellidos")
            self.id_field.value = user_data.get("matricula") # Asumiendo que user y matricula son lo mismo o similar
            self.role_dropdown.value = self._get_role_string(user_data.get("role"))
            
            # Buscamos el ID del depto para seleccionarlo
            if user_data.get("departamento_id"):
                self.dept_dropdown.value = str(user_data.get("departamento_id"))
        else:
            # -- MODO CREACIÓN --
            # Solo mostramos los campos de contraseña si estamos creando uno nuevo
            password_section = ft.Row(
                controls=[self.password_field, self.confirm_pass_field],
                spacing=15
            )

        # ==================== LAYOUT (2 COLUMNAS) ====================
        self.content = ft.Column(
            controls=[
                # Sección 1: Cuenta
                ft.Text("Datos de Cuenta", weight=ft.FontWeight.BOLD, color=styles.PRIMARY_BLUE),
                ft.Row([self.username_field, self.role_dropdown], spacing=15),
                
                # Aquí se insertan los campos de contraseña (solo en crear)
                password_section,

                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

                # Sección 2: Perfil
                ft.Text("Información Personal", weight=ft.FontWeight.BOLD, color=styles.PRIMARY_BLUE),
                ft.Row([self.name_field, self.lastname_field], spacing=15),
                ft.Row([self.id_field, self.dept_dropdown], spacing=15),
            ],
            width=600, # Hacemos el formulario más ancho para las 2 columnas
            height=450,
            scroll=ft.ScrollMode.AUTO
        )

        self.actions = [
            ft.OutlinedButton("Cancelar", on_click=self.close_dialog, style=ft.ButtonStyle(color=styles.TEXT_COLOR, side=ft.BorderSide(1, ft.Colors.GREY_300), shape=ft.RoundedRectangleBorder(radius=8)), height=45),
            ft.ElevatedButton("Guardar", on_click=self._save_data, style=ft.ButtonStyle(bgcolor=styles.PRIMARY_BLUE, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8)), height=45),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _load_departments(self):
        depts = dept_controller.get_all_departments()
        options = []
        for d in depts:
            options.append(ft.dropdown.Option(key=str(d.id), text=d.nombre))
        self.dept_dropdown.options = options

    def _get_role_string(self, role_val):
        # Helper por si el rol viene como int o string
        if isinstance(role_val, int):
            return {1: "Básico", 2: "Gerente", 3: "Administrador"}.get(role_val, "Básico")
        return role_val

    def _clear_error(self, e):
        if e.control.error_text:
            e.control.error_text = None
            e.control.update()

    def _save_data(self, e):
        # 1. Recolección
        user = self.username_field.value
        pwd = self.password_field.value
        pwd_confirm = self.confirm_pass_field.value
        nombre = self.name_field.value
        apellidos = self.lastname_field.value
        matricula = self.id_field.value
        rol = self.role_dropdown.value
        depto_val = self.dept_dropdown.value

        # 2. Validaciones Generales
        has_error = False
        
        if not user:
            self.username_field.error_text = "Requerido"
            has_error = True
        
        if not nombre:
            self.name_field.error_text = "Requerido"
            has_error = True
            
        if not apellidos:
            self.lastname_field.error_text = "Requerido"
            has_error = True
            
        if not matricula:
            self.id_field.error_text = "Requerido"
            has_error = True
            
        if not rol:
            self.role_dropdown.error_text = "Requerido"
            has_error = True
            
        if not depto_val:
            self.dept_dropdown.error_text = "Requerido"
            has_error = True
            
        if has_error:
            self.page.update()
            return

        # 3. Validación de Contraseña (Solo Creación)
        if not self.user_data:
            if not pwd:
                self.password_field.error_text = "Requerida"
                has_error = True
            elif pwd != pwd_confirm:
                self.confirm_pass_field.error_text = "No coinciden"
                has_error = True
                
            if has_error:
                self.page.update()
                return

        # 4. Llamar al Controlador
        result = None
        if self.user_data:
            # UPDATE
            result = controller.update_user(
                db_id=self.user_data.get("id"),
                nombre=nombre,
                apellidos=apellidos,
                matricula=matricula, # Usamos el campo matricula
                role=rol,
                dept_id=int(depto_val)
            )
        else:
            # CREATE
            result = controller.create_user(
                username=user,
                raw_password=pwd,
                nombre=nombre,
                apellidos=apellidos,
                matricula=matricula,
                role=rol,
                dept_id=int(depto_val)
            )

        # 5. Manejo de Resultado
        if result["status"] == "success":
            self.close_dialog(None)
            
            def on_aviso_close(e):
                if self.on_success: self.on_success()
            
            # Usamos tu componente Aviso de éxito
            aviso = Aviso(self.page, message=result["message"], is_error=False, on_dismiss=on_aviso_close)
            aviso.show()
        else:
            # Si es error de duplicado, intentamos asignarlo al campo
            msg = result["message"].lower()
            if "usuario" in msg or "login" in msg:
                self.username_field.error_text = result["message"]
                self.username_field.update()
            elif "matrícula" in msg:
                self.id_field.error_text = result["message"]
                self.id_field.update()
            else:
                # Usamos tu componente Aviso de error para otros casos
                self._show_error_aviso(result["message"])

    def _show_error_aviso(self, msg):
        aviso = Aviso(self.page, message=msg, is_error=True)
        aviso.show()

    def show(self):
        self.page.open(self)

    def open_dialog(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)