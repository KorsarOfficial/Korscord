import os
import json
import shutil
from pathlib import Path
import psutil
import time
import win32gui
import win32process
import win32api
import win32con
import subprocess

class DiscordController:
    def __init__(self):
        print("Инициализация Discord контроллера...")
        self.app_data = os.getenv('APPDATA')
        self.local_app_data = os.getenv('LOCALAPPDATA')
        self.core_path = self.find_core_path()
        self.last_css = None
        
        if not self.core_path:
            raise Exception("Не найден путь к core.asar")
            
        print(f"Найден core.asar: {self.core_path}")
        self.inject_dynamic_code()
        print("Discord контроллер инициализирован")

    def find_core_path(self):
        discord_paths = [
            os.path.join(self.app_data, 'Discord'),
            os.path.join(self.local_app_data, 'Discord'),
        ]
        
        for discord_path in discord_paths:
            print(f"Поиск в {discord_path}")
            if os.path.exists(discord_path):
                app_dirs = [d for d in os.listdir(discord_path) if d.startswith('app-')]
                if app_dirs:
                    latest_app = max(app_dirs)
                    modules_path = os.path.join(discord_path, latest_app, 'modules')
                    
                    if os.path.exists(modules_path):
                        core_dirs = [d for d in os.listdir(modules_path) if d.startswith('discord_desktop_core')]
                        if core_dirs:
                            latest_core = max(core_dirs)
                            core_path = os.path.join(modules_path, latest_core, 'discord_desktop_core')
                            if os.path.exists(core_path):
                                print(f"Найден путь к core: {core_path}")
                                return core_path
        return None

    def inject_dynamic_code(self):
        try:
            # Создаем файл для динамического обновления темы
            theme_updater = """
const electron = require('electron');
const fs = require('fs');
const path = require('path');

// Путь к файлу с текущей темой
const themePath = path.join(__dirname, 'current_theme.css');

// Функция для применения темы
function applyTheme(css) {
    const windows = electron.BrowserWindow.getAllWindows();
    windows.forEach(win => {
        if (!win.isDestroyed()) {
            win.webContents.executeJavaScript(`
                (function() {
                    let style = document.getElementById('dynamic-theme');
                    if (!style) {
                        style = document.createElement('style');
                        style.id = 'dynamic-theme';
                        document.head.appendChild(style);
                    }
                    style.textContent = \`${css}\`;
                })();
            `);
        }
    });
}

// Следим за изменениями файла темы
fs.watchFile(themePath, { interval: 100 }, () => {
    try {
        const css = fs.readFileSync(themePath, 'utf8');
        applyTheme(css);
    } catch (error) {
        console.error('Error updating theme:', error);
    }
});

module.exports = require('./core.asar');
"""
            
            # Записываем код обновления
            index_path = os.path.join(self.core_path, 'index.js')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(theme_updater)
            
            # Создаем пустой файл темы
            theme_path = os.path.join(self.core_path, 'current_theme.css')
            if not os.path.exists(theme_path):
                with open(theme_path, 'w', encoding='utf-8') as f:
                    f.write('')
            
            print("Установлен код для динамического обновления")
            
        except Exception as e:
            print(f"Ошибка установки кода: {e}")

    def update_theme(self, primary_color, secondary_color, tertiary_color):
        try:
            def get_brightness(color):
                color = color.lstrip('#')
                rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                return (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000

            def get_contrast_color(background_color):
                brightness = get_brightness(background_color)
                if brightness > 180:  # Очень светлый фон
                    return '#000000'  # Черный текст
                elif brightness > 125:  # Светлый фон
                    return '#1a1a1a'  # Темно-серый текст
                elif brightness < 50:  # Очень темный фон
                    return '#ffffff'  # Белый текст
                else:  # Темный фон
                    return '#e0e0e0'  # Светло-серый текст

            # Определяем цвета текста для разных областей
            primary_text = get_contrast_color(primary_color)
            secondary_text = get_contrast_color(secondary_color)
            tertiary_text = get_contrast_color(tertiary_color)
            
            css = f"""
@keyframes textTransition {{
    0% {{
        color: var(--old-text-color);
        opacity: 1;
    }}
    50% {{
        opacity: 0.7;
    }}
    100% {{
        opacity: 1;
    }}
}}

@keyframes backgroundFill {{
    0% {{
        --background-primary: var(--old-background-primary);
        --background-secondary: var(--old-background-secondary);
        --background-tertiary: var(--old-background-tertiary);
        --text-normal: var(--old-text-normal);
        --text-muted: var(--old-text-muted);
    }}
    100% {{
        --background-primary: {primary_color};
        --background-secondary: {secondary_color};
        --background-tertiary: {tertiary_color};
        --text-normal: {primary_text};
        --text-muted: {secondary_text};
    }}
}}

:root {{
    /* Сохраняем старые значения */
    --old-background-primary: var(--background-primary, #36393f);
    --old-background-secondary: var(--background-secondary, #2f3136);
    --old-background-tertiary: var(--background-tertiary, #202225);
    --old-text-normal: var(--text-normal, #dcddde);
    --old-text-muted: var(--text-muted, #72767d);
    
    /* Применяем анимации */
    animation: backgroundFill 0.5s ease-in-out forwards;
    
    /* Устанавливаем новые цвета */
    --background-primary: {primary_color} !important;
    --background-secondary: {secondary_color} !important;
    --background-tertiary: {tertiary_color} !important;
    --background-floating: {secondary_color} !important;
    
    /* Адаптивные цвета текста */
    --text-normal: {primary_text} !important;
    --text-muted: {secondary_text} !important;
    --header-primary: {primary_text} !important;
    --interactive-normal: {secondary_text} !important;
    --interactive-active: {primary_text} !important;
    --interactive-hover: {primary_text} !important;
    --channel-text: {secondary_text} !important;
    
    /* Модификаторы */
    --background-modifier-hover: {tertiary_color} !important;
    --background-modifier-active: {primary_color} !important;
    --background-modifier-selected: {primary_color} !important;
}}

/* Анимация для текстовых элементов */
.markup-eYLPri,
.title-17SveM,
.name-28HaxV,
.username-3JLfHz,
.channelName-3KPsGw,
.headerText-1qIDDT,
.nameAndDecorators-3ERwy2,
.name-3Uvkvr {{
    animation: textTransition 0.7s ease-in-out forwards !important;
    color: {primary_text} !important;
}}

/* Каналы и категории */
.name-3Vmqxm {{
    color: {secondary_text} !important;
    transition: color 0.3s ease-in-out !important;
}}

/* Плавные переходы */
* {{
    transition: background-color 0.5s ease-in-out,
                border-color 0.5s ease-in-out,
                color 0.5s ease-in-out !important;
}}

/* Эффект появления текста */
@keyframes textAppear {{
    0% {{
        transform: translateY(5px);
        opacity: 0;
    }}
    100% {{
        transform: translateY(0);
        opacity: 1;
    }}
}}

/* Новые сообщения */
.message-2CShn3 {{
    animation: textAppear 0.3s ease-out forwards;
}}

/* Улучшенная читаемость */
.markup-eYLPri,
.title-17SveM,
.username-3JLfHz {{
    text-shadow: 0 1px 1px {primary_text}20;
}}

/* Подсветка при наведении */
.markup-eYLPri:hover,
.username-3JLfHz:hover {{
    opacity: 0.9;
    transition: opacity 0.2s ease-in-out;
}}

/* Ссылки */
.anchor-1MIwyf {{
    color: {primary_text} !important;
    opacity: 0.8;
    transition: opacity 0.2s ease-in-out !important;
}}

.anchor-1MIwyf:hover {{
    opacity: 1;
    text-decoration: underline;
}}
"""

            if css == self.last_css:
                return True

            self.last_css = css

            # Записываем новую тему в файл
            theme_path = os.path.join(self.core_path, 'current_theme.css')
            with open(theme_path, 'w', encoding='utf-8') as f:
                f.write(css)

            print(f"Тема обновлена с адаптивным текстом (яркость фона: {get_brightness(primary_color)})")
            return True

        except Exception as e:
            print(f"Ошибка обновления темы: {str(e)}")
            return False

    def __del__(self):
        try:
            theme_path = os.path.join(self.core_path, 'current_theme.css')
            if os.path.exists(theme_path):
                os.remove(theme_path)
        except:
            pass 
            pass 