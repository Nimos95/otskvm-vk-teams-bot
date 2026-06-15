# src/core/module_manager.py

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Optional, Tuple, Callable

class ModuleManager:
    """Менеджер модулей - загружает и управляет модулями бота"""
    
    def __init__(self, bot):
        self.bot = bot
        self.modules: Dict[str, object] = {}
        self.commands: Dict[str, Tuple[str, Callable]] = {}
    
    def load_all_modules(self):
        """Автоматически находит и загружает все модули из папки modules/"""
        # Путь к папке modules
        modules_path = Path(__file__).parent.parent / 'modules'
        
        print(f"🔍 Поиск модулей в {modules_path}")
        
        # Перебираем все папки в modules/
        for finder, name, ispkg in pkgutil.iter_modules([str(modules_path)]):
            # Пропускаем служебные папки
            if name.startswith('_'):
                continue
            
            self._load_module(name)
    
    def _load_module(self, module_name: str):
        """Загружает один модуль по имени"""
        try:
            print(f"📥 Загрузка модуля '{module_name}'...")
            
            # Импортируем модуль
            module = importlib.import_module(f'src.modules.{module_name}.handlers')
            
            # Вызываем функцию setup() если она есть
            if hasattr(module, 'setup'):
                module.setup(self.bot, self)
            
            self.modules[module_name] = module
            print(f"✅ Модуль '{module_name}' успешно загружен")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки модуля '{module_name}': {e}")
    
    def register_command(self, command_name: str, handler_func: Callable, module_name: str):
        """
        Регистрирует команду.
        
        Args:
            command_name: название команды (например '/start')
            handler_func: функция-обработчик
            module_name: имя модуля (для отладки)
        """
        self.commands[command_name.lower()] = (module_name, handler_func)
        print(f"   📌 Зарегистрирована команда {command_name} (модуль: {module_name})")
    
    def get_command_handler(self, command_name: str) -> Optional[Tuple[str, Callable]]:
        """Возвращает обработчик команды или None"""
        return self.commands.get(command_name.lower())
    
    def get_commands_list(self) -> Dict[str, str]:
        """Возвращает список всех команд с их модулями (для /help)"""
        result = {}
        for cmd, (module, _) in self.commands.items():
            result[cmd] = module
        return result