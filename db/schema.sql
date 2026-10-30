-- PostgreSQL схема ИС автомойки (соответствует разделу 9 SAD)

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    phone         VARCHAR(20) UNIQUE NOT NULL,
    email         VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20) NOT NULL DEFAULT 'client'
        CHECK (role IN ('client','washer','manager','admin')),
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cars (
    id       SERIAL PRIMARY KEY,
    user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    brand    VARCHAR(100),
    model    VARCHAR(100),
    plate    VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS services (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    price       NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id      SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    car_id  INTEGER REFERENCES cars(id),
    date    DATE,
    time    TIME,
    status  VARCHAR(50) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','pending_payment','paid','in_progress','done','cancelled'))
);

CREATE TABLE IF NOT EXISTS order_services (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES services(id),
    quantity   INTEGER NOT NULL DEFAULT 1,
    price      NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_stages (
    id        SERIAL PRIMARY KEY,
    order_id  INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    washer_id INTEGER REFERENCES users(id),
    stage     VARCHAR(50),
    date      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    id       SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    amount   NUMERIC(10,2) NOT NULL,
    status   VARCHAR(50) NOT NULL DEFAULT 'pending',
    date     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviews (
    id       SERIAL PRIMARY KEY,
    order_id  INTEGER UNIQUE NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id),
    rating    INTEGER CHECK (rating BETWEEN 1 AND 5),
    text      TEXT
);

INSERT INTO services (name, description, price) VALUES
 ('Экспресс-мойка', 'Кузов + сушка', 500),
 ('Комплексная мойка', 'Кузов, салон, сушка', 1200),
 ('Химчистка салона', 'Глубокая чистка', 3500)
ON CONFLICT DO NOTHING;