INSERT INTO permissions (id, name, resource_type, description)
VALUES
    -- System permissions
    (gen_random_uuid(), 'can_manage_access', 'system', 'Управление системным доступом'),
    (gen_random_uuid(), 'can_create', 'system', 'Создание системных объектов'),
    (gen_random_uuid(), 'can_edit', 'system', 'Редактирование системных объектов'),
    (gen_random_uuid(), 'can_delete', 'system', 'Удаление системных объектов'),
    (gen_random_uuid(), 'can_view', 'system', 'Просмотр системных объектов'),

    -- User permissions
    (gen_random_uuid(), 'can_manage_access', 'user', 'Управление доступом пользователей'),
    (gen_random_uuid(), 'can_create', 'user', 'Создание пользователей'),
    (gen_random_uuid(), 'can_edit', 'user', 'Редактирование пользователей'),
    (gen_random_uuid(), 'can_delete', 'user', 'Удаление пользователей'),
    (gen_random_uuid(), 'can_view', 'user', 'Просмотр пользователей'),

    -- Hotel permissions
    (gen_random_uuid(), 'can_create', 'hotel', 'Создание отелей'),
    (gen_random_uuid(), 'can_edit', 'hotel', 'Редактирование отелей'),
    (gen_random_uuid(), 'can_delete', 'hotel', 'Удаление отелей'),
    (gen_random_uuid(), 'can_view', 'hotel', 'Просмотр отелей'),

    -- Room permissions
    (gen_random_uuid(), 'can_create', 'room', 'Создание комнат'),
    (gen_random_uuid(), 'can_edit', 'room', 'Редактирование комнат'),
    (gen_random_uuid(), 'can_delete', 'room', 'Удаление комнат'),
    (gen_random_uuid(), 'can_view', 'room', 'Просмотр комнат'),

    -- Booking permissions
    (gen_random_uuid(), 'can_create', 'booking', 'Создание бронирований'),
    (gen_random_uuid(), 'can_edit', 'booking', 'Редактирование бронирований'),
    (gen_random_uuid(), 'can_view', 'booking', 'Просмотр бронирований'),
    (gen_random_uuid(), 'can_delete', 'booking', 'Удаление бронирований'),

    -- Comment permissions
    (gen_random_uuid(), 'can_create', 'comment', 'Создание комментариев'),
    (gen_random_uuid(), 'can_edit', 'comment', 'Редактирование комментариев'),
    (gen_random_uuid(), 'can_delete', 'comment', 'Удаление комментариев'),
    (gen_random_uuid(), 'can_view', 'comment', 'Просмотр комментариев')
ON CONFLICT (name, resource_type) DO NOTHING;


INSERT INTO roles (id, name, description)
VALUES
    (gen_random_uuid(), 'admin', 'Администратор системы'),
    (gen_random_uuid(), 'manager', 'Менеджер отеля'),
    (gen_random_uuid(), 'user', 'Обычный пользователь')
ON CONFLICT (name) DO NOTHING;

-- ADMIN permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'admin'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- MANAGER permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'manager'
  AND (
      (p.resource_type = 'user' AND p.name = 'can_view')
      OR (p.resource_type = 'hotel' AND p.name IN ('can_view', 'can_create', 'can_edit', 'can_delete'))
      OR (p.resource_type = 'room' AND p.name IN ('can_view', 'can_create', 'can_edit', 'can_delete'))
      OR (p.resource_type = 'booking' AND p.name IN ('can_view', 'can_edit'))
      OR (p.resource_type = 'comment' AND p.name = 'can_view')
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- USER permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'user'
  AND (
      (p.resource_type = 'user' AND p.name = 'can_view')
      OR (p.resource_type = 'hotel' AND p.name = 'can_view')
      OR (p.resource_type = 'room' AND p.name = 'can_view')
      OR (p.resource_type = 'booking' AND p.name IN ('can_create', 'can_edit', 'can_view'))
      OR (p.resource_type = 'comment' AND p.name IN ('can_create', 'can_edit', 'can_view', 'can_delete'))
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;
