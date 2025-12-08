import flet as ft

# Paleta de colores
BG_COLOR = "#F4F7FC"
SIDEBAR_BG = "#FFFFFF"
PRIMARY_BLUE = "#3B82F6"
TEXT_COLOR = "#374151"
# Colores Base
PRIMARY_BLUE = "#3B82F6" # Blue 500
TEXT_COLOR = "#1F2937" # Gray 800
BG_COLOR = "#F3F4F6" # Gray 100 (Main Background)

# Sidebar
SIDEBAR_BG = "#111827" # Gray 900 (Dark Navy)
SIDEBAR_TEXT = "#E5E7EB" # Gray 200
SIDEBAR_TEXT_SELECTED = "#FFFFFF"
SIDEBAR_ICON_SELECTED = "#3B82F6"

# Cards
CARD_BG = "#FFFFFF"
CARD_SHADOW = ft.BoxShadow(
    spread_radius=1,
    blur_radius=5,
    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
    offset=ft.Offset(0, 1),
)

# Botones Dashboard
BTN_PRIMARY_BG = "#3B82F6" # Azul (Crear)
BTN_MODIFY_BG = "#F59E0B" # Amarillo/Naranja (Modificar)
BTN_DELETE_BG = "#EF4444" # Rojo (Eliminar)

# Otros Botones
BTN_COMPLETE_BG = "#10B981" # Verde (Completar)
BTN_TEXT_WHITE = "#FFFFFF"

# Status Badges
STATUS_GREEN_BG = "#D1FAE5"
STATUS_GREEN_TXT = "#065F46"
STATUS_YELLOW_BG = "#FEF3C7"
STATUS_YELLOW_TXT = "#92400E"

def apply_theme(page: ft.Page):
    page.bgcolor = BG_COLOR
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Poppins")