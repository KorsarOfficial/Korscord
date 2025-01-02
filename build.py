import os
import shutil
import PyInstaller.__main__
import sys

def cleanup():
    """Очистка временных файлов и директорий"""
    print("Начало очистки...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"Удаление директории: {dir_name}")
            shutil.rmtree(dir_name)
    
    for file_ext in files_to_remove:
        for file in os.listdir('.'):
            if file.endswith(file_ext):
                print(f"Удаление файла: {file}")
                os.remove(file)
    print("Очистка завершена")

def build():
    """Сборка проекта"""
    print(f"Python версия: {sys.version}")
    print(f"Текущая директория: {os.getcwd()}")
    
    print("Очистка старых файлов...")
    cleanup()
    
    print("Начало сборки...")
    try:
        PyInstaller.__main__.run([
            'main.py',
            '--onefile',
            '--name=DiscordDynamicTheme',
            '--clean',
            '--debug=all'  # Добавляем отладочную информацию
        ])
        
        # Проверяем создание файла
        expected_exe = os.path.join('dist', 'DiscordDynamicTheme.exe')
        if os.path.exists(expected_exe):
            print(f"Файл успешно создан: {expected_exe}")
            print(f"Размер файла: {os.path.getsize(expected_exe)} байт")
        else:
            print("Ошибка: EXE файл не был создан")
            print("Содержимое папки dist:")
            if os.path.exists('dist'):
                print(os.listdir('dist'))
            else:
                print("Папка dist не существует")
                
    except Exception as e:
        print(f"Ошибка при сборке: {e}")
    
    print("Процесс сборки завершен")

if __name__ == "__main__":
    build() 