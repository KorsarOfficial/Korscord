import sys
import os
from cx_Freeze import setup, Executable

# Зависимости, которые нужно включить
build_exe_options = {
    "packages": ["numpy", "PIL", "sklearn", "requests"],
    "excludes": [],
    "include_files": []
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Используем Win32GUI для запуска без консоли

setup(
    name="Discord Dynamic Theme",
    version="1.0",
    description="Discord Dynamic Theme Changer",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="DiscordDynamicTheme.exe",
            icon="icon.ico"  # Добавьте свою иконку, если нужно
        )
    ]
) 