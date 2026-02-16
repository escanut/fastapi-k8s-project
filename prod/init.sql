CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO products (name, description, price) VALUES
    ('Laptop', 'A macbook pro m2', 1500),
    ('Mouse', 'A Mx master 3 fom Logitech', 25),
    ('Keyboard', 'A overpriced mechanical keyboard from razer', 80);

