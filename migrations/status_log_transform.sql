-- Изменяем тип поля reported_by на VARCHAR(255)
ALTER TABLE status_log ALTER COLUMN reported_by TYPE VARCHAR(255);