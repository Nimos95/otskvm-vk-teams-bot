# src/core/chat_filter.py

def is_private_chat(chat_id) -> bool:
    """
    Определяет, является ли чат личным в корпоративном VK Workspace.
    
    Примеры:
    - Личный чат: "moskvin_nr@spbstu.ru" (email пользователя)
    - Групповой чат: "692529003@chat.agent" (заканчивается на @chat.agent)
    """
    chat_id_str = str(chat_id)
    
    # Групповые чаты всегда заканчиваются на @chat.agent
    if chat_id_str.endswith('@chat.agent'):
        return False
    
    # В корпоративной версии личные чаты - это email'ы (содержат @)
    if '@' in chat_id_str:
        return True
    
    # Если ID - просто число (для обратной совместимости)
    if chat_id_str.isdigit():
        return True
    
    return False

def get_chat_type_name(chat_id) -> str:
    """Возвращает понятное название типа чата для логов"""
    chat_id_str = str(chat_id)
    
    if chat_id_str.endswith('@chat.agent'):
        return "групповой чат"
    elif '@' in chat_id_str:
        return "личный чат (корпоративный)"
    elif chat_id_str.isdigit():
        return "личный чат (обычный)"
    else:
        return "неизвестный тип"