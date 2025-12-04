import flet as ft

# Paleta de colores
BG_COLOR = "#F4F7FC"
SIDEBAR_BG = "#FFFFFF"
PRIMARY_BLUE = "#3B82F6"
TEXT_COLOR = "#374151"
STATUS_GREEN_BG = "#D1FAE5"
STATUS_GREEN_TXT = "#065F46"
STATUS_YELLOW_BG = "#FEF3C7"
STATUS_YELLOW_TXT = "#92400E"

# Botones de Acción
BTN_PRIMARY_BG = "#3B82F6"       # Azul (Crear/Registrar)
BTN_MODIFY_BG = "#F59E0B"        # Amarillo/Naranja (Modificar)
BTN_DELETE_BG = "#EF4444"        # Rojo (Eliminar)
BTN_COMPLETE_BG = "#10B981"      # Verde (Completar)
BTN_TEXT_WHITE = "#FFFFFF"       # Texto Blanco

# Configuración de tema
def apply_theme(page: ft.Page):
    page.padding = 0
    page.bgcolor = BG_COLOR
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap"
    }
    page.theme = ft.Theme(font_family="Poppins")