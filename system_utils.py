"""
System utilities module for The Wizard.
Handles RAM optimization, disk operations, and system information.
Separated from UI for better maintainability and testing.
"""

import os
import sys
import shutil
import psutil
import platform
import logging
import ctypes
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from constants import SAFE_PROCESSES, TEMP_CATEGORIES, LOG_FILE

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('TheWizard')


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    success: bool
    files_deleted: int
    folders_deleted: int
    space_freed: int  # bytes
    errors: List[str]


@dataclass
class SystemInfo:
    """System information container."""
    os_name: str
    os_version: str
    processor: str
    ram_total_gb: float
    ram_available_gb: float
    ram_percent_used: float


@dataclass
class DiskInfo:
    """Disk information container."""
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float


def is_admin() -> bool:
    """
    Check if the application is running with administrator privileges.
    
    Returns:
        bool: True if running as admin, False otherwise.
    """
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception as e:
        logger.warning(f"Could not check admin status: {e}")
        return False


def get_system_drive() -> str:
    """
    Get the system drive path (cross-platform compatible).
    
    Returns:
        str: System drive path (e.g., 'C:\\' on Windows, '/' on Linux).
    """
    if platform.system() == 'Windows':
        return os.environ.get('SystemDrive', 'C:') + '\\'
    return '/'


def get_system_info() -> SystemInfo:
    """
    Collect comprehensive system information.
    
    Returns:
        SystemInfo: Dataclass containing system details.
    """
    memory = psutil.virtual_memory()
    
    return SystemInfo(
        os_name=platform.system(),
        os_version=platform.release(),
        processor=platform.processor() or "Unknown",
        ram_total_gb=round(memory.total / (1024 ** 3), 2),
        ram_available_gb=round(memory.available / (1024 ** 3), 2),
        ram_percent_used=memory.percent
    )


def get_disk_info(path: Optional[str] = None) -> DiskInfo:
    """
    Get disk usage information.
    
    Args:
        path: Path to check. If None, uses system drive.
    
    Returns:
        DiskInfo: Dataclass containing disk usage details.
    """
    if path is None:
        path = get_system_drive()
    
    try:
        usage = shutil.disk_usage(path)
        total_gb = usage.total / (1024 ** 3)
        used_gb = usage.used / (1024 ** 3)
        free_gb = usage.free / (1024 ** 3)
        percent_used = (usage.used / usage.total) * 100
        
        return DiskInfo(
            total_gb=round(total_gb, 2),
            used_gb=round(used_gb, 2),
            free_gb=round(free_gb, 2),
            percent_used=round(percent_used, 1)
        )
    except Exception as e:
        logger.error(f"Error getting disk info: {e}")
        return DiskInfo(0, 0, 0, 0)


def get_ram_info() -> Dict[str, float]:
    """
    Get detailed RAM information.
    
    Returns:
        Dict with RAM stats in GB and percentages.
    """
    memory = psutil.virtual_memory()
    
    return {
        'total_gb': round(memory.total / (1024 ** 3), 2),
        'available_gb': round(memory.available / (1024 ** 3), 2),
        'used_gb': round(memory.used / (1024 ** 3), 2),
        'percent_used': memory.percent,
        'percent_free': 100 - memory.percent,
    }


def get_running_processes() -> List[Dict]:
    """
    Get list of running processes with memory usage.
    
    Returns:
        List of dicts with process info, sorted by memory usage.
    """
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
        try:
            info = proc.info
            if info['memory_info']:
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'memory_percent': round(info['memory_percent'], 2),
                    'memory_mb': round(info['memory_info'].rss / (1024 ** 2), 2),
                    'is_safe': info['name'].lower() in [p.lower() for p in SAFE_PROCESSES]
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)


def optimize_ram_safe(
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Tuple[int, List[str]]:
    """
    Safely optimize RAM by terminating non-critical processes.
    Only terminates processes NOT in the safe list.
    
    Args:
        progress_callback: Optional callback(percent, message) for progress updates.
    
    Returns:
        Tuple of (processes_terminated, list_of_errors).
    """
    terminated = 0
    errors = []
    safe_list_lower = [p.lower() for p in SAFE_PROCESSES]
    
    processes = list(psutil.process_iter(['pid', 'name', 'memory_percent']))
    total = len(processes)
    
    logger.info("Starting safe RAM optimization")
    
    for i, proc in enumerate(processes):
        try:
            name = proc.info['name']
            if name and name.lower() not in safe_list_lower:
                # Only terminate high memory processes (> 1%)
                if proc.info['memory_percent'] and proc.info['memory_percent'] > 1.0:
                    proc.terminate()
                    terminated += 1
                    logger.info(f"Terminated: {name} (PID: {proc.info['pid']})")
            
            if progress_callback:
                percent = int((i + 1) / total * 100)
                progress_callback(percent, f"Analyse: {name or 'Unknown'}")
                
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            error_msg = f"Accès refusé: {proc.info.get('name', 'Unknown')}"
            errors.append(error_msg)
            logger.warning(error_msg)
        except Exception as e:
            error_msg = f"Erreur avec {proc.info.get('name', 'Unknown')}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    logger.info(f"RAM optimization complete. Terminated: {terminated}, Errors: {len(errors)}")
    return terminated, errors


def scan_temp_files(category: str = 'windows_temp') -> Tuple[int, int, int]:
    """
    Scan temporary files without deleting them.
    
    Args:
        category: Category of temp files to scan.
    
    Returns:
        Tuple of (file_count, folder_count, total_size_bytes).
    """
    file_count = 0
    folder_count = 0
    total_size = 0
    
    cat_info = TEMP_CATEGORIES.get(category, TEMP_CATEGORIES['windows_temp'])
    
    for path_key in cat_info['paths']:
        # Resolve environment variables
        if path_key in ['TEMP', 'TMP']:
            temp_dir = os.environ.get(path_key)
        elif 'APPDATA' in path_key:
            appdata = os.environ.get('APPDATA', '')
            temp_dir = path_key.replace('APPDATA', appdata)
        else:
            temp_dir = path_key
        
        if not temp_dir or not os.path.exists(temp_dir):
            continue
        
        try:
            # Use os.scandir for better performance
            with os.scandir(temp_dir) as entries:
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            file_count += 1
                            total_size += entry.stat().st_size
                        elif entry.is_dir(follow_symlinks=False):
                            folder_count += 1
                            # Calculate folder size
                            for root, dirs, files in os.walk(entry.path):
                                for f in files:
                                    try:
                                        fp = os.path.join(root, f)
                                        total_size += os.path.getsize(fp)
                                    except (OSError, IOError):
                                        pass
                    except (OSError, IOError):
                        pass
        except PermissionError:
            logger.warning(f"Permission denied scanning: {temp_dir}")
        except Exception as e:
            logger.error(f"Error scanning {temp_dir}: {e}")
    
    return file_count, folder_count, total_size


def clean_temp_files(
    category: str = 'windows_temp',
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> CleanupResult:
    """
    Clean temporary files from the specified category.
    
    Args:
        category: Category of temp files to clean.
        progress_callback: Optional callback(percent, message) for progress updates.
    
    Returns:
        CleanupResult with operation details.
    """
    files_deleted = 0
    folders_deleted = 0
    space_freed = 0
    errors = []
    
    cat_info = TEMP_CATEGORIES.get(category, TEMP_CATEGORIES['windows_temp'])
    
    logger.info(f"Starting cleanup for category: {category}")
    
    for path_key in cat_info['paths']:
        # Resolve environment variables
        if path_key in ['TEMP', 'TMP']:
            temp_dir = os.environ.get(path_key)
        elif 'APPDATA' in path_key:
            appdata = os.environ.get('APPDATA', '')
            temp_dir = path_key.replace('APPDATA', appdata)
        else:
            temp_dir = path_key
        
        if not temp_dir or not os.path.exists(temp_dir):
            continue
        
        try:
            entries = list(os.scandir(temp_dir))
            total = len(entries)
            
            for i, entry in enumerate(entries):
                try:
                    if entry.is_file(follow_symlinks=False):
                        size = entry.stat().st_size
                        os.unlink(entry.path)
                        files_deleted += 1
                        space_freed += size
                        logger.debug(f"Deleted file: {entry.path}")
                    elif entry.is_dir(follow_symlinks=False):
                        # Calculate folder size before deletion
                        folder_size = 0
                        for root, dirs, files in os.walk(entry.path):
                            for f in files:
                                try:
                                    folder_size += os.path.getsize(os.path.join(root, f))
                                except (OSError, IOError):
                                    pass
                        
                        shutil.rmtree(entry.path)
                        folders_deleted += 1
                        space_freed += folder_size
                        logger.debug(f"Deleted folder: {entry.path}")
                    
                    if progress_callback:
                        percent = int((i + 1) / total * 100)
                        progress_callback(percent, f"Nettoyage: {entry.name[:30]}")
                        
                except PermissionError:
                    error_msg = f"Accès refusé: {entry.name}"
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Erreur: {entry.name} - {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    
        except PermissionError:
            errors.append(f"Accès refusé au dossier: {temp_dir}")
            logger.warning(f"Permission denied for directory: {temp_dir}")
        except Exception as e:
            errors.append(f"Erreur dossier: {temp_dir} - {str(e)}")
            logger.error(f"Error processing {temp_dir}: {e}")
    
    logger.info(f"Cleanup complete. Files: {files_deleted}, Folders: {folders_deleted}, Space: {space_freed} bytes")
    
    return CleanupResult(
        success=len(errors) == 0,
        files_deleted=files_deleted,
        folders_deleted=folders_deleted,
        space_freed=space_freed,
        errors=errors
    )


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string.
    
    Args:
        bytes_value: Size in bytes.
    
    Returns:
        Formatted string (e.g., '1.5 GB', '250 MB').
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def get_gpu_info() -> Optional[Dict]:
    """
    Try to get GPU information (NVIDIA or basic Windows info).
    
    Returns:
        Dict with GPU info or None if not available.
    """
    gpu_info = {'available': False, 'name': 'Non détecté', 'memory': None}
    
    # Try NVIDIA first
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu',
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(', ')
            if len(parts) >= 5:
                gpu_info = {
                    'available': True,
                    'name': parts[0],
                    'memory_total_mb': int(parts[1]),
                    'memory_used_mb': int(parts[2]),
                    'memory_free_mb': int(parts[3]),
                    'utilization_percent': int(parts[4]),
                }
                return gpu_info
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass
    
    # Try Windows WMI as fallback
    try:
        if platform.system() == 'Windows':
            import subprocess
            result = subprocess.run(
                ['wmic', 'path', 'win32_videocontroller', 'get', 'name'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = [l.strip() for l in result.stdout.split('\n') if l.strip() and l.strip() != 'Name']
                if lines:
                    gpu_info = {
                        'available': True,
                        'name': lines[0],
                        'memory': None  # WMI doesn't give reliable memory info
                    }
    except Exception:
        pass
    
    return gpu_info
