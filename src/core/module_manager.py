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
        self.callbacks: Dict[str, Tuple[str, Callable]] = {}  # <-- НОВОЕ
    
    def load_all_modules(self):
        """Автоматически находит и загружает все модули из папки modules/"""
        modules_path = Path(__file__).parent.parent / 'modules'
        
        print(f"🔍 Поиск модулей в {modules_path}")
        
        if not modules_path.exists():
            print(f"⚠️ Папка modules не найдена: {modules_path}")
            return
        
        for finder, name, ispkg in pkgutil.iter_modules([str(modules_path)]):
            if name.startswith('_'):
                continue
            self._load_module(name)
    
    def _load_module(self, module_name: str):
        """Загружает один модуль по имени"""
        try:
            print(f"📥 Загрузка модуля '{module_name}'...")
            
            module = importlib.import_module(f'src.modules.{module_name}.handlers')
            
            if hasattr(module, 'setup'):
                module.setup(
                    bot=self.bot,
                    module_manager=self
                )
            
            self.modules[module_name] = module
            print(f"✅ Модуль '{module_name}' успешно загружен")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки модуля '{module_name}': {e}")
    
    def register_command(self, command_name: str, handler_func: Callable, module_name: str):
        """Регистрирует команду"""
        self.commands[command_name.lower()] = (module_name, handler_func)
        print(f"   📌 Зарегистрирована команда {command_name} (модуль: {module_name})")
    
    def register_callback(self, callback_data: str, handler_func: Callable, module_name: str):
        """Регистрирует обработчик callback-кнопок"""
        self.callbacks[callback_data] = (module_name, handler_func)
        print(f"   📌 Зарегистрирован callback {callback_data} (модуль: {module_name})")
    
    def get_command_handler(self, command_name: str) -> Optional[Tuple[str, Callable]]:
        """Возвращает обработчик команды или None"""
        return self.commands.get(command_name.lower())
    
    def get_callback_handler(self, callback_data: str) -> Optional[Tuple[str, Callable]]:
        """Возвращает обработчик callback или None"""
        return self.callbacks.get(callback_data)