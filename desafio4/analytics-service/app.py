from flask import Flask, jsonify
from datetime import datetime
import requests
import os

app = Flask(__name__)

GARAGE_SERVICE_URL = os.getenv("GARAGE_SERVICE_URL", "http://garage-service:5100")


def get_cars_from_garage():
    try:
        response = requests.get(f"{GARAGE_SERVICE_URL}/cars", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("cars", [])
    except requests.exceptions.RequestException as e:
        return None


def calculate_price_class(price):
    if price < 150000:
        return "Economy"
    elif price < 300000:
        return "Mid-range"
    elif price < 600000:
        return "Luxury"
    else:
        return "Ultra-luxury"


def calculate_performance_class(horsepower):
    if horsepower < 600:
        return "Standard"
    elif horsepower < 900:
        return "High"
    else:
        return "Extreme"


def calculate_days_in_garage(added_at):
    try:
        added_date = datetime.fromisoformat(added_at)
        days = (datetime.now() - added_date).days
        return days
    except:
        return 0


def get_status_analysis(status):
    status_map = {
        "available": "Ready for use",
        "racing": "Currently in competition",
        "maintenance": "Under maintenance",
        "sold": "No longer in inventory",
    }
    return status_map.get(status, "Unknown status")


@app.route("/")
def index():
    return jsonify(
        {
            "service": "Analytics Service",
            "description": "Forza Garage - Analytics & Reports API",
            "version": "1.0.0",
            "emoji": "📊",
            "endpoints": {
                "GET /": "Service information",
                "GET /report": "Complete report of all cars",
                "GET /report/<id>": "Detailed report of a specific car",
                "GET /summary": "Executive summary with aggregations",
                "GET /activity": "Activity analysis",
                "GET /health": "Health check (includes Garage Service)",
            },
            "garage_service": GARAGE_SERVICE_URL,
        }
    )


@app.route("/report")
def get_report():
    cars = get_cars_from_garage()

    if cars is None:
        return (
            jsonify(
                {
                    "error": "Unable to connect to Garage Service",
                    "service": "Analytics Service",
                }
            ),
            503,
        )

    if not cars:
        return jsonify(
            {
                "service": "Analytics Service",
                "report_type": "complete",
                "total_cars": 0,
                "message": "No cars in garage",
            }
        )

    enriched_cars = []
    for car in cars:
        enriched_car = car.copy()
        enriched_car["analytics"] = {
            "price_class": calculate_price_class(car["price"]),
            "performance_class": calculate_performance_class(car["horsepower"]),
            "value_per_hp": round(car["price"] / car["horsepower"], 2),
            "days_in_garage": calculate_days_in_garage(car.get("added_at", "")),
            "status_analysis": get_status_analysis(car["status"]),
        }
        enriched_cars.append(enriched_car)

    return jsonify(
        {
            "service": "Analytics Service",
            "report_type": "complete",
            "total_cars": len(enriched_cars),
            "timestamp": datetime.now().isoformat(),
            "cars": enriched_cars,
        }
    )


@app.route("/report/<int:car_id>")
def get_car_report(car_id):
    cars = get_cars_from_garage()

    if cars is None:
        return (
            jsonify(
                {
                    "error": "Unable to connect to Garage Service",
                    "service": "Analytics Service",
                }
            ),
            503,
        )

    car = next((c for c in cars if c["id"] == car_id), None)

    if not car:
        return (
            jsonify(
                {
                    "error": "Car not found",
                    "car_id": car_id,
                    "service": "Analytics Service",
                }
            ),
            404,
        )

    acceleration_score = max(0, 100 - (car["acceleration"] - 2.0) * 20)
    speed_score = min(100, (car["top_speed"] / 250) * 100)
    power_score = min(100, (car["horsepower"] / 1500) * 100)
    performance_score = (acceleration_score + speed_score + power_score) / 3

    sorted_by_power = sorted(cars, key=lambda x: x["horsepower"], reverse=True)
    ranking = next(
        (i + 1 for i, c in enumerate(sorted_by_power) if c["id"] == car_id), 0
    )

    same_category = [c for c in cars if c["category"] == car["category"]]
    if len(same_category) > 0:
        avg_category_hp = sum(c["horsepower"] for c in same_category) / len(
            same_category
        )
        avg_category_speed = sum(c["top_speed"] for c in same_category) / len(
            same_category
        )

        hp_diff = ((car["horsepower"] - avg_category_hp) / avg_category_hp) * 100
        speed_diff = (
            (car["top_speed"] - avg_category_speed) / avg_category_speed
        ) * 100
    else:
        hp_diff = 0
        speed_diff = 0

    recommendations = []
    if performance_score > 90:
        recommendations.append("Excellent overall performance")
    if acceleration_score > 95:
        recommendations.append("Top acceleration in category")
    if car["price"] < 200000 and car["horsepower"] > 600:
        recommendations.append("Outstanding value for money")
    if car["horsepower"] > 900:
        recommendations.append("Extreme power output")
    if car["status"] == "available":
        recommendations.append("Ready for immediate deployment")

    return jsonify(
        {
            "service": "Analytics Service",
            "report_type": "detailed",
            "car_id": car_id,
            "manufacturer": car["manufacturer"],
            "model": car["model"],
            "basic_info": {
                "year": car["year"],
                "category": car["category"],
                "status": car["status"],
                "price": car["price"],
            },
            "performance_metrics": {
                "horsepower": car["horsepower"],
                "top_speed": car["top_speed"],
                "acceleration": car["acceleration"],
            },
            "detailed_analysis": {
                "performance_score": round(performance_score, 2),
                "acceleration_score": round(acceleration_score, 2),
                "speed_score": round(speed_score, 2),
                "power_score": round(power_score, 2),
                "ranking_in_garage": ranking,
                "total_cars": len(cars),
            },
            "category_comparison": {
                "category": car["category"],
                "cars_in_category": len(same_category),
                "vs_category_avg_hp": f"{hp_diff:+.1f}%",
                "vs_category_avg_speed": f"{speed_diff:+.1f}%",
            },
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/summary")
def get_summary():
    cars = get_cars_from_garage()

    if cars is None:
        return (
            jsonify(
                {
                    "error": "Unable to connect to Garage Service",
                    "service": "Analytics Service",
                }
            ),
            503,
        )

    if not cars:
        return jsonify(
            {
                "service": "Analytics Service",
                "summary_type": "executive",
                "message": "No cars in garage",
            }
        )

    total_value = sum(car["price"] for car in cars)
    avg_hp = sum(car["horsepower"] for car in cars) / len(cars)
    avg_speed = sum(car["top_speed"] for car in cars) / len(cars)
    avg_price = total_value / len(cars)
    avg_acceleration = sum(car["acceleration"] for car in cars) / len(cars)

    by_category = {}
    for car in cars:
        category = car["category"]
        if category not in by_category:
            by_category[category] = {"count": 0, "total_hp": 0, "total_price": 0}
        by_category[category]["count"] += 1
        by_category[category]["total_hp"] += car["horsepower"]
        by_category[category]["total_price"] += car["price"]

    category_summary = {}
    for category, data in by_category.items():
        category_summary[category] = {
            "count": data["count"],
            "avg_hp": round(data["total_hp"] / data["count"], 2),
            "avg_price": round(data["total_price"] / data["count"], 2),
        }

    by_status = {}
    for car in cars:
        status = car["status"]
        by_status[status] = by_status.get(status, 0) + 1

    by_manufacturer = {}
    for car in cars:
        manufacturer = car["manufacturer"]
        by_manufacturer[manufacturer] = by_manufacturer.get(manufacturer, 0) + 1

    most_powerful = max(cars, key=lambda x: x["horsepower"])
    fastest = max(cars, key=lambda x: x["top_speed"])
    quickest = min(cars, key=lambda x: x["acceleration"])
    most_expensive = max(cars, key=lambda x: x["price"])
    best_value = min(cars, key=lambda x: x["price"] / x["horsepower"])

    insights = []
    if len(cars) >= 10:
        insights.append(f"Garage has a substantial collection of {len(cars)} cars")
    if avg_hp > 700:
        insights.append("High-performance focus with average HP above 700")
    if total_value > 3000000:
        insights.append("Premium inventory with total value over $3M")
    available_count = by_status.get("available", 0)
    if available_count > len(cars) * 0.5:
        insights.append(f"Good availability: {available_count} cars ready for use")

    return jsonify(
        {
            "service": "Analytics Service",
            "summary_type": "executive",
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "total_cars": len(cars),
                "total_value": total_value,
                "avg_horsepower": round(avg_hp, 2),
                "avg_top_speed": round(avg_speed, 2),
                "avg_price": round(avg_price, 2),
                "avg_acceleration": round(avg_acceleration, 2),
            },
            "by_category": category_summary,
            "by_status": by_status,
            "by_manufacturer": by_manufacturer,
            "top_performers": {
                "most_powerful": f"{most_powerful['manufacturer']} {most_powerful['model']} ({most_powerful['horsepower']} HP)",
                "fastest": f"{fastest['manufacturer']} {fastest['model']} ({fastest['top_speed']} mph)",
                "quickest": f"{quickest['manufacturer']} {quickest['model']} ({quickest['acceleration']}s 0-60)",
                "most_expensive": f"{most_expensive['manufacturer']} {most_expensive['model']} (${most_expensive['price']:,})",
                "best_value": f"{best_value['manufacturer']} {best_value['model']} (${round(best_value['price']/best_value['horsepower'], 2)}/HP)",
            },
            "insights": insights,
        }
    )


@app.route("/activity")
def get_activity():
    cars = get_cars_from_garage()

    if cars is None:
        return (
            jsonify(
                {
                    "error": "Unable to connect to Garage Service",
                    "service": "Analytics Service",
                }
            ),
            503,
        )

    if not cars:
        return jsonify(
            {
                "service": "Analytics Service",
                "activity_type": "operational",
                "message": "No cars in garage",
            }
        )

    active_statuses = ["available", "racing"]
    active_cars = [c for c in cars if c["status"] in active_statuses]
    inactive_cars = [c for c in cars if c["status"] not in active_statuses]

    utilization_rate = (len(active_cars) / len(cars)) * 100 if cars else 0

    racing_count = sum(1 for c in cars if c["status"] == "racing")
    maintenance_count = sum(1 for c in cars if c["status"] == "maintenance")
    available_count = sum(1 for c in cars if c["status"] == "available")
    sold_count = sum(1 for c in cars if c["status"] == "sold")

    avg_hp_available = sum(
        c["horsepower"] for c in cars if c["status"] == "available"
    ) / max(available_count, 1)
    total_racing_power = sum(c["horsepower"] for c in cars if c["status"] == "racing")

    category_analysis = {}
    for car in cars:
        category = car["category"]
        if category not in category_analysis:
            category_analysis[category] = {
                "total": 0,
                "available": 0,
                "racing": 0,
                "maintenance": 0,
            }

        category_analysis[category]["total"] += 1
        if car["status"] == "available":
            category_analysis[category]["available"] += 1
        elif car["status"] == "racing":
            category_analysis[category]["racing"] += 1
        elif car["status"] == "maintenance":
            category_analysis[category]["maintenance"] += 1

    for category, data in category_analysis.items():
        data["availability_rate"] = round((data["available"] / data["total"]) * 100, 2)

    alerts = []
    if maintenance_count > 0:
        alerts.append(f"{maintenance_count} car(s) in maintenance need attention")
    if utilization_rate < 50:
        alerts.append(f"Low utilization rate: {round(utilization_rate, 1)}%")
    if available_count >= 5:
        alerts.append(f"High-value inventory available ({available_count} cars)")
    if sold_count > len(cars) * 0.2:
        alerts.append(f"Significant inventory turnover: {sold_count} cars sold")

    return jsonify(
        {
            "service": "Analytics Service",
            "activity_type": "operational",
            "timestamp": datetime.now().isoformat(),
            "utilization": {
                "total_cars": len(cars),
                "active_cars": len(active_cars),
                "inactive_cars": len(inactive_cars),
                "utilization_rate": round(utilization_rate, 2),
                "available_count": available_count,
                "racing_count": racing_count,
                "maintenance_count": maintenance_count,
                "sold_count": sold_count,
            },
            "efficiency_metrics": {
                "avg_hp_per_available_car": round(avg_hp_available, 2),
                "total_racing_power": total_racing_power,
                "maintenance_backlog": maintenance_count,
            },
            "category_analysis": category_analysis,
            "alerts": alerts,
        }
    )


@app.route("/health")
def health():
    timestamp = datetime.now().isoformat()

    try:
        start_time = datetime.now()
        response = requests.get(f"{GARAGE_SERVICE_URL}/health", timeout=5)
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000

        if response.status_code == 200:
            garage_status = "healthy"
            connectivity = "ok"
        else:
            garage_status = "unhealthy"
            connectivity = "degraded"
    except requests.exceptions.RequestException as e:
        garage_status = "unreachable"
        connectivity = "failed"
        latency = 0

    analytics_status = "healthy"

    overall_healthy = garage_status == "healthy" and analytics_status == "healthy"

    return jsonify(
        {
            "service": "Analytics Service",
            "analytics_service": analytics_status,
            "garage_service": garage_status,
            "connectivity": connectivity,
            "latency_ms": round(latency, 2) if latency else None,
            "overall": "healthy" if overall_healthy else "degraded",
            "timestamp": timestamp,
        }
    ), (200 if overall_healthy else 503)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5101))
    app.run(host="0.0.0.0", port=port, debug=True)
