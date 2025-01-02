import os
import re
import asar
import json
import base64
import shutil
from pathlib import Path

class DiscordPatcher:
    def __init__(self):
        self.app_data = os.getenv('APPDATA')
        self.local_app_data = os.getenv('LOCALAPPDATA')
        
    def patch_core(self, discord_path):
        try:
            # Находим core.asar
            core_path = None
            for root, dirs, files in os.walk(discord_path):
                if 'core.asar' in files:
                    core_path = os.path.join(root, 'core.asar')
                    break
            
            if not core_path:
                return False
                
            # Создаем резервную копию
            if not os.path.exists(core_path + '.backup'):
                shutil.copy2(core_path, core_path + '.backup')
            
            # Распаковываем asar
            asar.extract(core_path, 'core_temp')
            
            # Модифицируем main.js
            main_js_path = os.path.join('core_temp', 'app', 'mainScreen.js')
            if os.path.exists(main_js_path):
                with open(main_js_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Отключаем проверки целостности
                content = content.replace('if (!Utils.isValidTheme()', 'if (false')
                content = content.replace('validateTheme', 'function(){return true}')
                
                with open(main_js_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Пересобираем asar
            asar.pack('core_temp', core_path)
            
            # Очищаем временные файлы
            shutil.rmtree('core_temp')
            
            return True
            
        except Exception as e:
            print(f"Ошибка патча: {str(e)}")
            return False
    
    def patch_settings(self, settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Отключаем проверки тем
            settings['DANGEROUS_ENABLE_DEVTOOLS_ONLY_ENABLE_IF_YOU_KNOW_WHAT_YOURE_DOING'] = True
            settings['enableDevTools'] = True
            settings['validateThemes'] = False
            settings['allowCustomThemes'] = True
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Ошибка патча настроек: {str(e)}")
            return False 