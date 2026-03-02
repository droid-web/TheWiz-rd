"""
The Wizard - Optimiseur Gamer
Main application with modern gamer-themed Tkinter interface.

Features:
- Safe RAM optimization
- Temp files cleaning with preview
- Disk status monitoring
- System information display
- GPU information (if available)
- Logging and error tracking
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import time

# Import our modules
from constants import COLORS, FONTS, WINDOW
from system_utils import (
    get_system_info, get_disk_info, get_ram_info, get_gpu_info,
    optimize_ram_safe, scan_temp_files, clean_temp_files,
    format_bytes, is_admin, get_running_processes
)


class ModernButton(tk.Canvas):
    """
    Custom modern button with hover effects and optional icon.
    """
    def __init__(self, parent, text: str, command: callable, 
                 icon: str = "", width: int = 200, height: int = 45,
                 accent_color: str = COLORS['accent_cyan']):
        super().__init__(parent, width=width, height=height, 
                        bg=COLORS['bg_dark'], highlightthickness=0)
        
        self.text = text
        self.icon = icon
        self.command = command
        self.width = width
        self.height = height
        self.accent = accent_color
        self.hover = False
        
        self._draw()
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
    
    def _draw(self):
        """Draw the button."""
        self.delete('all')
        
        # Background
        bg = COLORS['bg_button_hover'] if self.hover else COLORS['bg_button']
        border = self.accent if self.hover else COLORS['bg_light']
        
        # Rounded rectangle
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                radius=10, fill=bg, outline=border, width=2)
        
        # Icon and text
        display_text = f"{self.icon}  {self.text}" if self.icon else self.text
        text_color = self.accent if self.hover else COLORS['text_primary']
        
        self.create_text(self.width//2, self.height//2, 
                        text=display_text, fill=text_color,
                        font=FONTS['button'])
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self.hover = True
        self._draw()
        self.config(cursor='hand2')
    
    def _on_leave(self, event):
        self.hover = False
        self._draw()
    
    def _on_click(self, event):
        if self.command:
            self.command()


class ProgressDialog(tk.Toplevel):
    """
    Modern progress dialog with animated progress bar.
    """
    def __init__(self, parent, title: str = "Opération en cours"):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x150")
        self.configure(bg=COLORS['bg_dark'])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")
        
        # Status label
        self.status_label = tk.Label(
            self, text="Initialisation...",
            font=FONTS['label'], fg=COLORS['text_secondary'],
            bg=COLORS['bg_dark']
        )
        self.status_label.pack(pady=(20, 10))
        
        # Progress bar style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Gamer.Horizontal.TProgressbar",
            troughcolor=COLORS['bg_medium'],
            background=COLORS['accent_cyan'],
            darkcolor=COLORS['accent_cyan'],
            lightcolor=COLORS['accent_blue'],
            bordercolor=COLORS['bg_light'],
            thickness=20
        )
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self, style="Gamer.Horizontal.TProgressbar",
            length=350, mode='determinate'
        )
        self.progress.pack(pady=10)
        
        # Percentage label
        self.percent_label = tk.Label(
            self, text="0%",
            font=FONTS['subtitle'], fg=COLORS['accent_cyan'],
            bg=COLORS['bg_dark']
        )
        self.percent_label.pack(pady=5)
    
    def update_progress(self, percent: int, status: str = ""):
        """Update progress bar and status."""
        self.progress['value'] = percent
        self.percent_label.config(text=f"{percent}%")
        if status:
            # Truncate long status messages
            if len(status) > 45:
                status = status[:42] + "..."
            self.status_label.config(text=status)
        self.update()


class TheWizardApp:
    """
    Main application class for The Wizard optimizer.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW['title'])
        self.root.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.root.minsize(WINDOW['min_width'], WINDOW['min_height'])
        self.root.configure(bg=COLORS['bg_dark'])
        
        # Check admin status
        self.is_admin = is_admin()
        
        # Cache system info
        self._system_info = None
        self._last_update = 0
        
        self._setup_ui()
        self._update_stats()
    
    def _setup_ui(self):
        """Setup the main user interface."""
        # Header
        self._create_header()
        
        # Stats panel
        self._create_stats_panel()
        
        # Buttons
        self._create_buttons()
        
        # Footer
        self._create_footer()
    
    def _create_header(self):
        """Create the header section with title."""
        header_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        header_frame.pack(fill='x', pady=(20, 10))
        
        # Title with glow effect (using multiple labels)
        title_text = "⚡ THE WIZARD ⚡"
        
        title = tk.Label(
            header_frame, text=title_text,
            font=FONTS['title'], fg=COLORS['accent_cyan'],
            bg=COLORS['bg_dark']
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame, text="Optimiseur Gaming Avancé",
            font=FONTS['subtitle'], fg=COLORS['text_secondary'],
            bg=COLORS['bg_dark']
        )
        subtitle.pack()
        
        # Admin status indicator
        admin_text = "✓ Mode Administrateur" if self.is_admin else "⚠ Mode Standard (droits limités)"
        admin_color = COLORS['success'] if self.is_admin else COLORS['warning']
        
        admin_label = tk.Label(
            header_frame, text=admin_text,
            font=FONTS['small'], fg=admin_color,
            bg=COLORS['bg_dark']
        )
        admin_label.pack(pady=(5, 0))
    
    def _create_stats_panel(self):
        """Create the statistics panel showing system status."""
        stats_frame = tk.Frame(self.root, bg=COLORS['bg_medium'], padx=20, pady=15)
        stats_frame.pack(fill='x', padx=30, pady=15)
        
        # Title
        tk.Label(
            stats_frame, text="📊 État du Système",
            font=FONTS['subtitle'], fg=COLORS['accent_blue'],
            bg=COLORS['bg_medium']
        ).pack(anchor='w')
        
        # Stats container
        container = tk.Frame(stats_frame, bg=COLORS['bg_medium'])
        container.pack(fill='x', pady=(10, 0))
        
        # RAM stats
        self.ram_frame = tk.Frame(container, bg=COLORS['bg_light'], padx=15, pady=10)
        self.ram_frame.pack(side='left', expand=True, fill='both', padx=(0, 5))
        
        tk.Label(
            self.ram_frame, text="💾 RAM",
            font=FONTS['label'], fg=COLORS['accent_purple'],
            bg=COLORS['bg_light']
        ).pack(anchor='w')
        
        self.ram_label = tk.Label(
            self.ram_frame, text="Chargement...",
            font=FONTS['mono'], fg=COLORS['text_primary'],
            bg=COLORS['bg_light'], justify='left'
        )
        self.ram_label.pack(anchor='w')
        
        self.ram_bar = ttk.Progressbar(
            self.ram_frame, length=150, mode='determinate'
        )
        self.ram_bar.pack(fill='x', pady=(5, 0))
        
        # Disk stats
        self.disk_frame = tk.Frame(container, bg=COLORS['bg_light'], padx=15, pady=10)
        self.disk_frame.pack(side='left', expand=True, fill='both', padx=(5, 0))
        
        tk.Label(
            self.disk_frame, text="💿 Disque",
            font=FONTS['label'], fg=COLORS['accent_green'],
            bg=COLORS['bg_light']
        ).pack(anchor='w')
        
        self.disk_label = tk.Label(
            self.disk_frame, text="Chargement...",
            font=FONTS['mono'], fg=COLORS['text_primary'],
            bg=COLORS['bg_light'], justify='left'
        )
        self.disk_label.pack(anchor='w')
        
        self.disk_bar = ttk.Progressbar(
            self.disk_frame, length=150, mode='determinate'
        )
        self.disk_bar.pack(fill='x', pady=(5, 0))
    
    def _create_buttons(self):
        """Create the action buttons."""
        button_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        button_frame.pack(pady=20)
        
        # Row 1
        row1 = tk.Frame(button_frame, bg=COLORS['bg_dark'])
        row1.pack(pady=5)
        
        ModernButton(
            row1, text="Optimiser RAM", icon="🚀",
            command=self._optimize_ram,
            accent_color=COLORS['accent_purple']
        ).pack(side='left', padx=10)
        
        ModernButton(
            row1, text="Nettoyer Fichiers Temp", icon="🗑️",
            command=self._clean_temp,
            accent_color=COLORS['accent_pink']
        ).pack(side='left', padx=10)
        
        # Row 2
        row2 = tk.Frame(button_frame, bg=COLORS['bg_dark'])
        row2.pack(pady=5)
        
        ModernButton(
            row2, text="Infos Système", icon="ℹ️",
            command=self._show_system_info,
            accent_color=COLORS['accent_blue']
        ).pack(side='left', padx=10)
        
        ModernButton(
            row2, text="Infos GPU", icon="🎮",
            command=self._show_gpu_info,
            accent_color=COLORS['accent_green']
        ).pack(side='left', padx=10)
        
        # Row 3
        row3 = tk.Frame(button_frame, bg=COLORS['bg_dark'])
        row3.pack(pady=5)
        
        ModernButton(
            row3, text="Actualiser Stats", icon="🔄",
            command=self._update_stats,
            accent_color=COLORS['accent_cyan'],
            width=420
        ).pack(padx=10)
    
    def _create_footer(self):
        """Create the footer section."""
        footer = tk.Frame(self.root, bg=COLORS['bg_dark'])
        footer.pack(side='bottom', fill='x', pady=10)
        
        tk.Label(
            footer, text="The Wizard v2.0 | Gamer Optimizer",
            font=FONTS['small'], fg=COLORS['text_muted'],
            bg=COLORS['bg_dark']
        ).pack()
    
    def _update_stats(self):
        """Update the statistics display."""
        # RAM info (dict)
        ram = get_ram_info()
        ram_text = f"{ram['used_gb']:.1f} / {ram['total_gb']:.1f} GB\n{ram['percent_used']:.0f}% utilisé"
        self.ram_label.config(text=ram_text)
        self.ram_bar['value'] = ram['percent_used']
        
        # Color code RAM bar
        if ram['percent_used'] > 90:
            self._style_bar('ram', COLORS['error'])
        elif ram['percent_used'] > 70:
            self._style_bar('ram', COLORS['warning'])
        else:
            self._style_bar('ram', COLORS['success'])
        
        # Disk info (dataclass - use dot notation)
        disk = get_disk_info()
        disk_text = f"{disk.used_gb:.1f} / {disk.total_gb:.1f} GB\n{disk.percent_used:.0f}% utilisé"
        self.disk_label.config(text=disk_text)
        self.disk_bar['value'] = disk.percent_used
        
        # Color code disk bar
        if disk.percent_used > 90:
            self._style_bar('disk', COLORS['error'])
        elif disk.percent_used > 80:
            self._style_bar('disk', COLORS['warning'])
        else:
            self._style_bar('disk', COLORS['success'])
    
    def _style_bar(self, bar_type: str, color: str):
        """Style a progress bar with a color."""
        style = ttk.Style()
        style_name = f"{bar_type}.Horizontal.TProgressbar"
        style.configure(
            style_name,
            troughcolor=COLORS['bg_medium'],
            background=color,
            darkcolor=color,
            lightcolor=color,
        )
        if bar_type == 'ram':
            self.ram_bar.configure(style=style_name)
        else:
            self.disk_bar.configure(style=style_name)
    
    def _optimize_ram(self):
        """Optimize RAM with progress dialog."""
        if not self.is_admin:
            if not messagebox.askyesno(
                "Avertissement",
                "Sans droits administrateur, certains processus ne pourront pas être terminés.\n\n"
                "Voulez-vous continuer en mode limité?"
            ):
                return
        
        # Confirmation
        processes = get_running_processes()
        non_safe = [p for p in processes if not p['is_safe'] and p['memory_percent'] > 1.0]
        
        if not messagebox.askyesno(
            "Confirmation",
            f"Cette opération va tenter de fermer {len(non_safe)} processus non-critiques.\n\n"
            "Les processus système et importants sont protégés.\n\n"
            "Continuer?"
        ):
            return
        
        # Show progress dialog
        progress = ProgressDialog(self.root, "Optimisation RAM")
        
        def run_optimization():
            terminated, errors = optimize_ram_safe(
                progress_callback=lambda p, s: self.root.after(0, progress.update_progress, p, s)
            )
            
            self.root.after(0, progress.destroy)
            self.root.after(0, self._update_stats)
            
            # Show result
            result_msg = f"✓ {terminated} processus terminés\n"
            if errors:
                result_msg += f"⚠ {len(errors)} erreurs (voir log)"
            
            self.root.after(0, lambda: messagebox.showinfo("Résultat", result_msg))
        
        threading.Thread(target=run_optimization, daemon=True).start()
    
    def _clean_temp(self):
        """Clean temporary files with preview."""
        # Scan first
        file_count, folder_count, total_size = scan_temp_files()
        
        if file_count == 0 and folder_count == 0:
            messagebox.showinfo("Info", "Aucun fichier temporaire à nettoyer!")
            return
        
        # Show preview
        size_str = format_bytes(total_size)
        if not messagebox.askyesno(
            "Aperçu du nettoyage",
            f"Fichiers trouvés: {file_count}\n"
            f"Dossiers trouvés: {folder_count}\n"
            f"Espace à libérer: {size_str}\n\n"
            "Supprimer ces fichiers?"
        ):
            return
        
        # Show progress
        progress = ProgressDialog(self.root, "Nettoyage en cours")
        
        def run_cleanup():
            result = clean_temp_files(
                progress_callback=lambda p, s: self.root.after(0, progress.update_progress, p, s)
            )
            
            self.root.after(0, progress.destroy)
            self.root.after(0, self._update_stats)
            
            freed_str = format_bytes(result.space_freed)
            result_msg = f"✓ {result.files_deleted} fichiers supprimés\n"
            result_msg += f"✓ {result.folders_deleted} dossiers supprimés\n"
            result_msg += f"✓ {freed_str} libérés\n"
            if result.errors:
                result_msg += f"\n⚠ {len(result.errors)} erreurs (certains fichiers en cours d'utilisation)"
            
            self.root.after(0, lambda: messagebox.showinfo("Résultat", result_msg))
        
        threading.Thread(target=run_cleanup, daemon=True).start()
    
    def _show_system_info(self):
        """Show system information dialog."""
        info = get_system_info()
        disk = get_disk_info()
        
        msg = f"🖥️ Système: {info.os_name} {info.os_version}\n"
        msg += f"⚙️ Processeur: {info.processor}\n\n"
        msg += f"💾 RAM Totale: {info.ram_total_gb} GB\n"
        msg += f"💾 RAM Disponible: {info.ram_available_gb} GB\n"
        msg += f"💾 RAM Utilisée: {info.ram_percent_used:.1f}%\n\n"
        msg += f"💿 Disque Total: {disk.total_gb} GB\n"
        msg += f"💿 Disque Utilisé: {disk.used_gb} GB ({disk.percent_used}%)\n"
        msg += f"💿 Disque Libre: {disk.free_gb} GB"
        
        messagebox.showinfo("Informations Système", msg)
    
    def _show_gpu_info(self):
        """Show GPU information dialog."""
        gpu = get_gpu_info()
        
        if not gpu or not gpu.get('available'):
            messagebox.showinfo(
                "Info GPU",
                "🎮 GPU: Non détecté ou informations non disponibles\n\n"
                "Note: Les informations détaillées nécessitent une carte NVIDIA avec nvidia-smi."
            )
            return
        
        msg = f"🎮 GPU: {gpu['name']}\n\n"
        
        if gpu.get('memory_total_mb'):
            msg += f"📊 Mémoire Totale: {gpu['memory_total_mb']} MB\n"
            msg += f"📊 Mémoire Utilisée: {gpu['memory_used_mb']} MB\n"
            msg += f"📊 Mémoire Libre: {gpu['memory_free_mb']} MB\n"
            msg += f"📊 Utilisation: {gpu['utilization_percent']}%"
        else:
            msg += "(Informations détaillées non disponibles)"
        
        messagebox.showinfo("Info GPU", msg)
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


def main():
    """Application entry point."""
    app = TheWizardApp()
    app.run()


if __name__ == "__main__":
    main()

 