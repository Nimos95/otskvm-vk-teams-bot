-- ============================================================
-- ПОЛНЫЙ СКРИПТ ПЕРЕСОЗДАНИЯ ТАБЛИЦЫ users
-- Версия: 1.0
-- Дата: 2026-06-19
-- Описание: Пересоздание таблицы users для VK Workspace бота
-- ============================================================

BEGIN;

-- ============================================================
-- 1. Сохраняем данные в временную таблицу (если они есть)
-- ============================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        CREATE TEMP TABLE users_backup AS SELECT * FROM users;
        RAISE NOTICE '✅ Данные users сохранены в временную таблицу';
    ELSE
        RAISE NOTICE '⚠️ Таблица users не существует, бэкап не требуется';
    END IF;
END $$;

-- ============================================================
-- 2. Удаляем старую таблицу users (если существует)
-- ============================================================
DROP TABLE IF EXISTS users CASCADE;
RAISE NOTICE '✅ Таблица users удалена';

-- ============================================================
-- 3. Создаём новую таблицу users
-- ============================================================
CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
RAISE NOTICE '✅ Таблица users создана';

-- ============================================================
-- 4. Добавляем комментарии к таблице и полям
-- ============================================================
COMMENT ON TABLE users IS 'Пользователи системы (VK Workspace)';
COMMENT ON COLUMN users.user_id IS 'ID пользователя (email из VK Workspace) PRIMARY KEY';
COMMENT ON COLUMN users.full_name IS 'Имя для отображения';
COMMENT ON COLUMN users.role IS 'Роль: superadmin / admin / manager / engineer / viewer';
COMMENT ON COLUMN users.created_at IS 'Когда зарегистрировался';
COMMENT ON COLUMN users.last_active IS 'Последняя активность';
COMMENT ON COLUMN users.is_active IS 'Активен ли пользователь';
RAISE NOTICE '✅ Комментарии добавлены';

-- ============================================================
-- 5. Добавляем индекс для быстрого поиска по роли
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
RAISE NOTICE '✅ Индекс idx_users_role создан';

-- ============================================================
-- 6. Восстанавливаем данные из бэкапа (если они были)
-- ============================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users_backup') THEN
        INSERT INTO users (user_id, full_name, role, created_at, last_active, is_active)
        SELECT user_id, full_name, role, created_at, last_active, is_active
        FROM users_backup
        ON CONFLICT (user_id) DO NOTHING;
        RAISE NOTICE '✅ Данные из бэкапа восстановлены';
        
        -- Удаляем временную таблицу
        DROP TABLE users_backup;
        RAISE NOTICE '✅ Временная таблица users_backup удалена';
    ELSE
        RAISE NOTICE '⚠️ Бэкап не найден, данные не восстанавливались';
    END IF;
END $$;

-- ============================================================
-- 7. Добавляем суперадминистратора
-- ============================================================
INSERT INTO users (user_id, full_name, role) 
VALUES ('moskvin_nr@spbstu.ru', 'Москвин Никита Романович', 'superadmin')
ON CONFLICT (user_id) DO UPDATE SET 
    role = 'superadmin',
    full_name = EXCLUDED.full_name;
RAISE NOTICE '✅ Суперадминистратор добавлен/обновлён';

-- ============================================================
-- 8. Проверка результатов
-- ============================================================
SELECT 
    '✅ Таблица users готова к работе' AS status,
    COUNT(*) AS total_users,
    COUNT(CASE WHEN role = 'superadmin' THEN 1 END) AS superadmins,
    COUNT(CASE WHEN role = 'admin' THEN 1 END) AS admins,
    COUNT(CASE WHEN role = 'manager' THEN 1 END) AS managers,
    COUNT(CASE WHEN role = 'engineer' THEN 1 END) AS engineers,
    COUNT(CASE WHEN role = 'viewer' THEN 1 END) AS viewers
FROM users;

-- ============================================================
-- 9. Показываем структуру таблицы
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- ============================================================
-- 10. Показываем список всех пользователей
-- ============================================================
SELECT user_id, full_name, role, created_at, is_active FROM users ORDER BY created_at;

-- ============================================================
-- Фиксация транзакции
-- ============================================================
COMMIT;

-- ============================================================
-- Финальное сообщение
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ ✅ ✅ СКРИПТ ВЫПОЛНЕН УСПЕШНО ✅ ✅ ✅';
    RAISE NOTICE 'Таблица users готова к использованию в боте VK Workspace';
END $$;