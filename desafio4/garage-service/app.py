from flask import Flask, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

cars_db = []
next_id = 1


def init_data():
    global next_id
    sample_cars = [
        {
            "manufacturer": "Ferrari",
            "model": "SF90 Stradale",
            "year": 2023,
            "horsepower": 986,
            "top_speed": 211,
            "acceleration": 2.5,
            "price": 625000,
            "status": "available",
            "category": "Hypercar",
        },
        {
            "manufacturer": "Lamborghini",
            "model": "Revuelto",
            "year": 2024,
            "horsepower": 1001,
            "top_speed": 217,
            "acceleration": 2.8,
            "price": 608000,
            "status": "available",
            "category": "Hypercar",
        },
        {
            "manufacturer": "Porsche",
            "model": "911 GT3 RS",
            "year": 2023,
            "horsepower": 518,
            "top_speed": 184,
            "acceleration": 3.0,
            "price": 241000,
            "status": "racing",
            "category": "Sports",
        },
        {
            "manufacturer": "McLaren",
            "model": "720S",
            "year": 2023,
            "horsepower": 710,
            "top_speed": 212,
            "acceleration": 2.7,
            "price": 310000,
            "status": "available",
            "category": "Supercar",
        },
        {
            "manufacturer": "Aston Martin",
            "model": "DBS Superleggera",
            "year": 2023,
            "horsepower": 715,
            "top_speed": 211,
            "acceleration": 3.2,
            "price": 316000,
            "status": "maintenance",
            "category": "Supercar",
        },
        {
            "manufacturer": "Mercedes-AMG",
            "model": "GT Black Series",
            "year": 2023,
            "horsepower": 720,
            "top_speed": 202,
            "acceleration": 3.1,
            "price": 325000,
            "status": "available",
            "category": "Supercar",
        },
        {
            "manufacturer": "Chevrolet",
            "model": "Corvette Z06",
            "year": 2023,
            "horsepower": 670,
            "top_speed": 194,
            "acceleration": 2.6,
            "price": 106000,
            "status": "available",
            "category": "Sports",
        },
        {
            "manufacturer": "Audi",
            "model": "R8 V10",
            "year": 2023,
            "horsepower": 602,
            "top_speed": 205,
            "acceleration": 3.1,
            "price": 148000,
            "status": "available",
            "category": "Sports",
        },
        {
            "manufacturer": "BMW",
            "model": "M8 Competition",
            "year": 2023,
            "horsepower": 617,
            "top_speed": 190,
            "acceleration": 3.0,
            "price": 133000,
            "status": "sold",
            "category": "Sports",
        },
        {
            "manufacturer": "Nissan",
            "model": "GT-R Nismo",
            "year": 2023,
            "horsepower": 600,
            "top_speed": 196,
            "acceleration": 2.5,
            "price": 215000,
            "status": "available",
            "category": "Sports",
        },
    ]

    for car in sample_cars:
        car["id"] = next_id
        car["added_at"] = datetime.now().isoformat()
        cars_db.append(car)
        next_id += 1


init_data()


@app.route("/")
def index():
    return jsonify(
        {
            "service": "Garage Service",
            "description": "Forza Garage - Inventory Management API",
            "version": "1.0.0",
            "emoji": "🏎️",
            "endpoints": {
                "GET /": "Service information",
                "GET /cars": "List all cars",
                "GET /cars/<id>": "Get car by ID",
                "POST /cars": "Add new car",
                "PUT /cars/<id>": "Update car",
                "DELETE /cars/<id>": "Delete car",
                "GET /stats": "Get inventory statistics",
                "GET /health": "Health check",
            },
            "total_cars": len(cars_db),
        }
    )


@app.route("/cars", methods=["GET"])
def get_cars():
    return jsonify(
        {"service": "Garage Service", "total": len(cars_db), "cars": cars_db}
    )


@app.route("/cars/<int:car_id>", methods=["GET"])
def get_car(car_id):
    car = next((c for c in cars_db if c["id"] == car_id), None)

    if car:
        return jsonify({"service": "Garage Service", "car": car})
    else:
        return jsonify({"error": "Car not found", "car_id": car_id}), 404


@app.route("/cars", methods=["POST"])
def add_car():
    global next_id

    data = request.get_json()

    required_fields = [
        "manufacturer",
        "model",
        "year",
        "horsepower",
        "top_speed",
        "acceleration",
        "price",
        "status",
        "category",
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    valid_statuses = ["available", "racing", "maintenance", "sold"]
    if data["status"] not in valid_statuses:
        return (
            jsonify(
                {
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                }
            ),
            400,
        )

    valid_categories = ["Hypercar", "Supercar", "Sports", "Luxury"]
    if data["category"] not in valid_categories:
        return (
            jsonify(
                {
                    "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}"
                }
            ),
            400,
        )

    new_car = {
        "id": next_id,
        "manufacturer": data["manufacturer"],
        "model": data["model"],
        "year": data["year"],
        "horsepower": data["horsepower"],
        "top_speed": data["top_speed"],
        "acceleration": data["acceleration"],
        "price": data["price"],
        "status": data["status"],
        "category": data["category"],
        "added_at": datetime.now().isoformat(),
    }

    cars_db.append(new_car)
    next_id += 1

    return (
        jsonify(
            {
                "service": "Garage Service",
                "message": "Car added successfully",
                "car": new_car,
            }
        ),
        201,
    )


@app.route("/cars/<int:car_id>", methods=["PUT"])
def update_car(car_id):
    car = next((c for c in cars_db if c["id"] == car_id), None)

    if not car:
        return jsonify({"error": "Car not found", "car_id": car_id}), 404

    data = request.get_json()

    if "status" in data:
        valid_statuses = ["available", "racing", "maintenance", "sold"]
        if data["status"] not in valid_statuses:
            return (
                jsonify(
                    {
                        "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                    }
                ),
                400,
            )

    if "category" in data:
        valid_categories = ["Hypercar", "Supercar", "Sports", "Luxury"]
        if data["category"] not in valid_categories:
            return (
                jsonify(
                    {
                        "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}"
                    }
                ),
                400,
            )

    updatable_fields = [
        "manufacturer",
        "model",
        "year",
        "horsepower",
        "top_speed",
        "acceleration",
        "price",
        "status",
        "category",
    ]

    for field in updatable_fields:
        if field in data:
            car[field] = data[field]

    return jsonify(
        {"service": "Garage Service", "message": "Car updated successfully", "car": car}
    )


@app.route("/cars/<int:car_id>", methods=["DELETE"])
def delete_car(car_id):
    global cars_db

    car = next((c for c in cars_db if c["id"] == car_id), None)

    if not car:
        return jsonify({"error": "Car not found", "car_id": car_id}), 404

    cars_db = [c for c in cars_db if c["id"] != car_id]

    return jsonify(
        {
            "service": "Garage Service",
            "message": "Car deleted successfully",
            "car_id": car_id,
            "deleted_car": car,
        }
    )


@app.route("/stats")
def get_stats():
    if not cars_db:
        return jsonify(
            {
                "service": "Garage Service",
                "message": "No cars in garage",
                "total_cars": 0,
            }
        )

    total_value = sum(car["price"] for car in cars_db)
    avg_hp = sum(car["horsepower"] for car in cars_db) / len(cars_db)
    avg_speed = sum(car["top_speed"] for car in cars_db) / len(cars_db)
    avg_price = total_value / len(cars_db)

    by_status = {}
    for car in cars_db:
        status = car["status"]
        by_status[status] = by_status.get(status, 0) + 1

    by_category = {}
    for car in cars_db:
        category = car["category"]
        by_category[category] = by_category.get(category, 0) + 1

    most_powerful = max(cars_db, key=lambda x: x["horsepower"])
    fastest = max(cars_db, key=lambda x: x["top_speed"])
    quickest = min(cars_db, key=lambda x: x["acceleration"])
    most_expensive = max(cars_db, key=lambda x: x["price"])

    return jsonify(
        {
            "service": "Garage Service",
            "overview": {
                "total_cars": len(cars_db),
                "total_value": total_value,
                "avg_horsepower": round(avg_hp, 2),
                "avg_top_speed": round(avg_speed, 2),
                "avg_price": round(avg_price, 2),
            },
            "by_status": by_status,
            "by_category": by_category,
            "extremes": {
                "most_powerful": f"{most_powerful['manufacturer']} {most_powerful['model']} ({most_powerful['horsepower']} HP)",
                "fastest": f"{fastest['manufacturer']} {fastest['model']} ({fastest['top_speed']} mph)",
                "quickest": f"{quickest['manufacturer']} {quickest['model']} ({quickest['acceleration']}s 0-60)",
                "most_expensive": f"{most_expensive['manufacturer']} {most_expensive['model']} (${most_expensive['price']:,})",
            },
        }
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "service": "Garage Service",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "cars_count": len(cars_db),
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5100))
    app.run(host="0.0.0.0", port=port, debug=True)
