import os
import json
import shutil
from pathlib import Path
import psutil  # добавим для работы с процессами
import time

class DiscordController:
    def __init__(self):
        print("Инициализация Discord контроллера...")
        self.app_data = os.getenv('APPDATA')
        self.local_app_data = os.getenv('LOCALAPPDATA')
        
        # Проверяем, запущен ли Discord
        if self.is_discord_running():
            print("ВНИМАНИЕ: Discord запущен. Закройте Discord и запустите программу снова.")
            raise Exception("Discord должен быть закрыт")
            
        self.core_path = self.find_core_path()
        if not self.core_path:
            raise Exception("Не найден путь к core.asar")
            
        print(f"Найден core.asar: {self.core_path}")
        
        # Делаем бэкап при первом запуске
        self.backup_discord_files()
        
        print("Discord контроллер инициализирован")

    def is_discord_running(self):
        for proc in psutil.process_iter(['name']):
            if 'discord' in proc.info['name'].lower():
                return True
        return False

    def find_core_path(self):
        discord_paths = [
            os.path.join(self.app_data, 'Discord'),
            os.path.join(self.local_app_data, 'Discord'),
        ]
        
        for discord_path in discord_paths:
            print(f"Поиск в {discord_path}")
            if os.path.exists(discord_path):
                # Ищем последнюю версию Discord
                app_dirs = [d for d in os.listdir(discord_path) if d.startswith('app-')]
                if app_dirs:
                    latest_app = max(app_dirs)
                    modules_path = os.path.join(discord_path, latest_app, 'modules')
                    
                    if os.path.exists(modules_path):
                        core_dirs = [d for d in os.listdir(modules_path) if d.startswith('discord_desktop_core')]
                        if core_dirs:
                            latest_core = max(core_dirs)
                            core_path = os.path.join(modules_path, latest_core, 'discord_desktop_core')
                            return core_path
        return None

    def backup_discord_files(self):
        if not os.path.exists('discord_backup'):
            print("Создание резервной копии файлов Discord...")
            try:
                os.makedirs('discord_backup')
                # Копируем важные файлы
                if self.core_path:
                    core_asar = os.path.join(self.core_path, 'core.asar')
                    if os.path.exists(core_asar):
                        shutil.copy2(core_asar, os.path.join('discord_backup', 'core.asar'))
                print("Резервная копия создана")
            except Exception as e:
                print(f"Ошибка при создании резервной копии: {e}")

    def update_theme(self, primary_color, secondary_color, tertiary_color):
        try:
            if not self.core_path:
                return False

            # Создаем CSS
            css = f"""
            :root {{
                --background-primary: {primary_color} !important;
                --background-secondary: {secondary_color} !important;
                --background-tertiary: {tertiary_color} !important;
                --background-floating: {secondary_color} !important;
                --header-primary: #fff !important;
                --interactive-active: #fff !important;
                --interactive-normal: #dcddde !important;
                --channeltextarea-background: {secondary_color} !important;
                --background-modifier-hover: {tertiary_color} !important;
                --background-modifier-active: {primary_color} !important;
                --background-modifier-selected: {primary_color} !important;
            }}
            """

            # Создаем инжектор
            injector = f"""
            module.exports = require('./core.asar');
            const fs = require('fs');
            const electron = require('electron');
            
            electron.app.on('ready', () => {{
                electron.session.defaultSession.webRequest.onHeadersReceived(
                    {{ urls: ['*://*.discord.com/*'] }},
                    (details, callback) => {{
                        callback({{
                            responseHeaders: {{
                                ...details.responseHeaders,
                                'Content-Security-Policy': ["*"]
                            }}
                        }});
                    }}
                );
            }});
            
            const style = `{css}`;
            
            electron.app.on('browser-window-created', (event, window) => {{
                window.webContents.on('dom-ready', () => {{
                    window.webContents.executeJavaScript(`
                        (() => {{
                            const style = document.createElement('style');
                            style.textContent = \`{css}\`;
                            document.head.appendChild(style);
                        }})();
                    `);
                }});
            }});
            """

            # Записываем инжектор
            index_path = os.path.join(self.core_path, 'index.js')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(injector)

            print("Тема обновлена. Перезапустите Discord.")
            return True

        except Exception as e:
            print(f"Ошибка обновления темы: {str(e)}")
            return False

    def restore_backup(self):
        try:
            if os.path.exists('discord_backup'):
                print("Восстановление файлов Discord из резервной копии...")
                if self.core_path:
                    backup_core = os.path.join('discord_backup', 'core.asar')
                    if os.path.exists(backup_core):
                        shutil.copy2(backup_core, os.path.join(self.core_path, 'core.asar'))
                print("Восстановление завершено")
        except Exception as e:
            print(f"Ошибка при восстановлении: {e}") 