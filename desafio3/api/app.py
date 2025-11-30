from flask import Flask, jsonify, request
import psycopg2
import redis
import os
import json
import time

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "forza_garage")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_db_connection():
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            return conn
        except psycopg2.OperationalError:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            time.sleep(1)


def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cars (
            id SERIAL PRIMARY KEY,
            manufacturer VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            year INTEGER NOT NULL,
            class VARCHAR(50) NOT NULL,
            horsepower INTEGER NOT NULL,
            top_speed INTEGER NOT NULL,
            acceleration DECIMAL(4, 2) NOT NULL,
            price INTEGER NOT NULL,
            rarity VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute("SELECT COUNT(*) FROM cars")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_cars = [
            ("Ferrari", "LaFerrari", 2013, "S2", 950, 217, 2.4, 1500000, "Legendary"),
            ("Lamborghini", "Aventador SVJ", 2019, "S2", 770, 217, 2.6, 520000, "Epic"),
            ("Porsche", "918 Spyder", 2014, "S2", 887, 214, 2.2, 850000, "Legendary"),
            ("McLaren", "P1", 2014, "S2", 903, 217, 2.7, 1150000, "Legendary"),
            ("Bugatti", "Chiron", 2018, "X", 1500, 261, 2.3, 3000000, "Legendary"),
            ("Koenigsegg", "Jesko", 2020, "X", 1600, 278, 2.5, 2800000, "Legendary"),
            ("Ford", "GT", 2017, "S1", 647, 216, 2.9, 450000, "Epic"),
            ("Nissan", "GT-R Nismo", 2020, "S1", 600, 196, 2.5, 175000, "Rare"),
            ("Chevrolet", "Corvette C8 Z06", 2023, "S1", 670, 194, 2.6, 110000, "Rare"),
            ("BMW", "M4 Competition", 2021, "A", 503, 180, 3.5, 75000, "Common"),
            ("Mercedes-AMG", "GT R", 2020, "S1", 577, 198, 3.5, 160000, "Rare"),
            ("Audi", "R8 V10 Plus", 2020, "S1", 602, 205, 3.1, 195000, "Rare"),
        ]

        for car in sample_cars:
            cursor.execute(
                """
                INSERT INTO cars (manufacturer, model, year, class, horsepower, 
                                top_speed, acceleration, price, rarity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                car,
            )

        conn.commit()

    cursor.close()
    conn.close()


@app.route("/")
def index():
    return jsonify(
        {
            "service": "Forza Garage API",
            "version": "1.0",
            "endpoints": {
                "/": "Service info",
                "/cars": "List all cars",
                "/cars/<id>": "Get car by ID",
                "/cars/class/<class>": "Get cars by class",
                "/cars/rarity/<rarity>": "Get cars by rarity",
                "/stats": "Garage statistics",
                "/health": "Health check",
            },
        }
    )


@app.route("/cars")
def get_cars():
    cache_key = "all_cars"
    cached = cache.get(cache_key)

    if cached:
        return jsonify({"source": "cache", "cars": json.loads(cached)})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars ORDER BY manufacturer, model")

    column_names = [desc[0] for desc in cursor.description]
    cars = []

    for row in cursor.fetchall():
        car = dict(zip(column_names, row))
        car["created_at"] = str(car["created_at"])
        car["acceleration"] = float(car["acceleration"])
        car["price"] = int(car["price"])
        cars.append(car)

    cursor.close()
    conn.close()

    cache.setex(cache_key, 60, json.dumps(cars))

    return jsonify({"source": "database", "total": len(cars), "cars": cars})


@app.route("/cars/<int:car_id>")
def get_car(car_id):
    cache_key = f"car_{car_id}"
    cached = cache.get(cache_key)

    if cached:
        return jsonify({"source": "cache", "car": json.loads(cached)})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))

    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return jsonify({"error": "Car not found"}), 404

    column_names = [desc[0] for desc in cursor.description]
    car = dict(zip(column_names, row))
    car["created_at"] = str(car["created_at"])
    car["acceleration"] = float(car["acceleration"])
    car["price"] = int(car["price"])

    cursor.close()
    conn.close()

    cache.setex(cache_key, 60, json.dumps(car))

    return jsonify({"source": "database", "car": car})


@app.route("/cars/class/<car_class>")
def get_cars_by_class(car_class):
    cache_key = f"class_{car_class}"
    cached = cache.get(cache_key)

    if cached:
        return jsonify(
            {"source": "cache", "class": car_class, "cars": json.loads(cached)}
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cars WHERE class = %s ORDER BY horsepower DESC", (car_class,)
    )

    column_names = [desc[0] for desc in cursor.description]
    cars = []

    for row in cursor.fetchall():
        car = dict(zip(column_names, row))
        car["created_at"] = str(car["created_at"])
        car["acceleration"] = float(car["acceleration"])
        car["price"] = int(car["price"])
        cars.append(car)

    cursor.close()
    conn.close()

    if not cars:
        return jsonify({"error": "No cars found for this class"}), 404

    cache.setex(cache_key, 60, json.dumps(cars))

    return jsonify(
        {"source": "database", "class": car_class, "total": len(cars), "cars": cars}
    )


@app.route("/cars/rarity/<rarity>")
def get_cars_by_rarity(rarity):
    cache_key = f"rarity_{rarity}"
    cached = cache.get(cache_key)

    if cached:
        return jsonify(
            {"source": "cache", "rarity": rarity, "cars": json.loads(cached)}
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cars WHERE rarity = %s ORDER BY price DESC", (rarity,)
    )

    column_names = [desc[0] for desc in cursor.description]
    cars = []

    for row in cursor.fetchall():
        car = dict(zip(column_names, row))
        car["created_at"] = str(car["created_at"])
        car["acceleration"] = float(car["acceleration"])
        car["price"] = int(car["price"])
        cars.append(car)

    cursor.close()
    conn.close()

    if not cars:
        return jsonify({"error": "No cars found for this rarity"}), 404

    cache.setex(cache_key, 60, json.dumps(cars))

    return jsonify(
        {"source": "database", "rarity": rarity, "total": len(cars), "cars": cars}
    )


@app.route("/stats")
def get_stats():
    cache_key = "garage_stats"
    cached = cache.get(cache_key)

    if cached:
        return jsonify({"source": "cache", "stats": json.loads(cached)})

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM cars")
    total_cars = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(horsepower) FROM cars")
    avg_hp = float(cursor.fetchone()[0] or 0)

    cursor.execute("SELECT AVG(price) FROM cars")
    avg_price = float(cursor.fetchone()[0] or 0)

    cursor.execute("SELECT MAX(top_speed) FROM cars")
    max_speed = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(acceleration) FROM cars")
    best_accel = float(cursor.fetchone()[0] or 0)

    cursor.execute(
        "SELECT class, COUNT(*) FROM cars GROUP BY class ORDER BY COUNT(*) DESC"
    )
    classes = [{"class": row[0], "count": row[1]} for row in cursor.fetchall()]

    cursor.execute(
        "SELECT rarity, COUNT(*) FROM cars GROUP BY rarity ORDER BY COUNT(*) DESC"
    )
    rarities = [{"rarity": row[0], "count": row[1]} for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    stats = {
        "total_cars": total_cars,
        "average_horsepower": round(avg_hp, 2),
        "average_price": round(avg_price, 2),
        "max_top_speed": max_speed,
        "best_acceleration": best_accel,
        "cars_by_class": classes,
        "cars_by_rarity": rarities,
    }

    cache.setex(cache_key, 30, json.dumps(stats))

    return jsonify({"source": "database", "stats": stats})


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()

        cache.ping()

        return jsonify(
            {"status": "healthy", "database": "connected", "cache": "connected"}
        )
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


if __name__ == "__main__":
    print("Inicializando Forza Garage API...")
    init_database()
    print("Banco de dados iniciado!")
    print("Subindo servidor Flask na porta 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)
