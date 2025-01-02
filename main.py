import time
import sys
import os
import ctypes
import subprocess
import traceback
from screen_analyzer import ScreenColorAnalyzer
from discord_controller import DiscordController
from config import UPDATE_INTERVAL, NUM_COLORS

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 50)
    print("Discord Dynamic Theme Controller")
    print("=" * 50)
    print("Нажмите Ctrl+C для выхода")
    print("-" * 50)

def run_main():
    try:
        # Устанавливаем кодировку Windows
        if sys.platform.startswith('win'):
            os.system('chcp 65001')
        
        clear_console()
        print_header()
        
        # Инициализация компонентов
        print("Инициализация...")
        try:
            screen_analyzer = ScreenColorAnalyzer()
            discord_controller = DiscordController()
        except Exception as e:
            print(f"\nОшибка инициализации: {str(e)}")
            print("\nПолный текст ошибки:")
            traceback.print_exc()
            input("\nНажмите Enter для выхода...")
            return
        
        print("\nУспешно подключено к Discord!")
        print("Начинаем мониторинг цветов рабочего стола...\n")
        
        update_counter = 0
        while True:
            try:
                update_counter += 1
                clear_console()
                print_header()
                
                print(f"Обновление #{update_counter}")
                colors = screen_analyzer.get_dominant_colors(NUM_COLORS)
                
                print("\nНайденные цвета:")
                for i, color in enumerate(colors, 1):
                    print(f"Цвет {i}: {color}")
                
                success = discord_controller.update_theme(
                    primary_color=colors[0],
                    secondary_color=colors[1],
                    tertiary_color=colors[2]
                )
                
                if success:
                    print("\n✓ Тема Discord успешно обновлена")
                else:
                    print("\n✗ Ошибка при обновлении темы Discord")
                
                print(f"\nСледующее обновление через {UPDATE_INTERVAL} секунд...")
                time.sleep(UPDATE_INTERVAL)
                
            except Exception as e:
                print(f"\nОшибка во время выполнения: {str(e)}")
                print("\nПолный текст ошибки:")
                traceback.print_exc()
                print("\nПовторная попытка через 5 секунд...")
                time.sleep(5)
                
    except KeyboardInterrupt:
        clear_console()
        print_header()
        print("\nПрограмма завершена пользователем")
        print("Спасибо за использование!")
        time.sleep(2)
    except Exception as e:
        print(f"\nКритическая ошибка: {str(e)}")
        print("\nПолный текст ошибки:")
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    if not is_admin():
        print("Запуск программы с правами администратора...")
        try:
            if ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1) > 32:
                sys.exit(0)
            else:
                print("Не удалось получить права администратора")
                input("Нажмите Enter для выхода...")
                sys.exit(1)
        except Exception as e:
            print(f"Ошибка при запросе прав администратора: {str(e)}")
            traceback.print_exc()
            input("Нажмите Enter для выхода...")
            sys.exit(1)
    else:
        run_main() 