INSERT INTO users (name, phone, password_hash, role)
VALUES ('Менеджер', '888',
        '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5',
        'manager')
ON CONFLICT (phone) DO UPDATE SET role = 'manager';