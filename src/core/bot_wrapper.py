# src/core/bot_wrapper.py

import time
import signal
from bot.bot import Bot


class SafeBot(Bot):
    """Обёртка над Bot с исправленной обработкой сигналов"""
    
    def idle(self):
        """
        Безопасная версия idle() без обработки сигналов.
        Используем простой цикл с проверкой флага.
        """
        self._running = True
        
        # Отключаем стандартную обработку сигналов
        try:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
        except:
            pass
        
        print("🤖 Бот запущен. Нажмите Ctrl+C для остановки.")
        
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self._running = False
            print("\n👋 Бот остановлен пользователем")
        finally:
            # Останавливаем поллинг
            try:
                self.stop_polling()
            except:
                pass