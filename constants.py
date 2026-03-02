"""
Constants and configuration for The Wizard application.
Centralized colors, paths, and settings for easy customization.
"""

# ==================== COLORS - GAMER THEME ====================
COLORS = {
    # Background colors
    'bg_dark': '#0d0d1a',
    'bg_medium': '#1a1a2e',
    'bg_light': '#16213e',
    'bg_button': '#1f4068',
    'bg_button_hover': '#2a5a8a',
    
    # Accent colors (neon gamer style)
    'accent_cyan': '#00ffcc',
    'accent_blue': '#00d4ff',
    'accent_purple': '#b429f9',
    'accent_pink': '#ff006e',
    'accent_green': '#39ff14',
    'accent_red': '#ff3131',
    'accent_orange': '#ff9500',
    
    # Text colors
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0c0',
    'text_muted': '#6c6c8a',
    
    # Status colors
    'success': '#39ff14',
    'warning': '#ff9500',
    'error': '#ff3131',
    'info': '#00d4ff',
}

# ==================== FONTS ====================
FONTS = {
    'title': ('Segoe UI', 24, 'bold'),
    'subtitle': ('Segoe UI', 14, 'bold'),
    'button': ('Segoe UI', 11, 'bold'),
    'label': ('Segoe UI', 10),
    'small': ('Segoe UI', 9),
    'mono': ('Consolas', 10),
}

# ==================== WINDOW SETTINGS ====================
WINDOW = {
    'title': 'The Wizard - Optimiseur Gamer',
    'width': 700,
    'height': 600,
    'min_width': 600,
    'min_height': 500,
}

# ==================== SAFE PROCESSES ====================
# Processes that should NEVER be terminated
SAFE_PROCESSES = [
    # Windows critical
    'system', 'system idle process', 'registry', 'smss.exe', 'csrss.exe',
    'wininit.exe', 'services.exe', 'lsass.exe', 'lsaiso.exe', 'svchost.exe',
    'winlogon.exe', 'dwm.exe', 'explorer.exe', 'taskhostw.exe', 'sihost.exe',
    'fontdrvhost.exe', 'ctfmon.exe', 'runtimebroker.exe', 'shellexperiencehost.exe',
    'startmenuexperienchost.exe', 'searchui.exe', 'searchapp.exe',
    'securityhealthservice.exe', 'securityhealthsystray.exe',
    'msmpeng.exe', 'nissrv.exe',  # Windows Defender
    'spoolsv.exe', 'audiodg.exe', 'conhost.exe', 'dllhost.exe',
    
    # Python (to keep app running)
    'python.exe', 'pythonw.exe', 'python3.exe', 'python',
    
    # GPU drivers
    'nvcontainer.exe', 'nvidia share.exe', 'nvdisplay.container.exe',
    'amdrsserv.exe', 'amd external events client module.exe',
    
    # Common important apps
    'discord.exe', 'slack.exe', 'teams.exe', 'spotify.exe',
]

# ==================== TEMP DIRECTORIES ====================
# Directories to clean for temporary files
TEMP_CATEGORIES = {
    'windows_temp': {
        'name': 'Windows Temp',
        'paths': ['TEMP', 'TMP'],
        'icon': '🗑️',
    },
    'prefetch': {
        'name': 'Prefetch',
        'paths': ['C:\\Windows\\Prefetch'],
        'icon': '⚡',
        'admin_required': True,
    },
    'recent': {
        'name': 'Recent Files',
        'paths': ['APPDATA\\Microsoft\\Windows\\Recent'],
        'icon': '📋',
    },
}

# ==================== LOG SETTINGS ====================
LOG_FILE = 'the_wizard.log'
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3
