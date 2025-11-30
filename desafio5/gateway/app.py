from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

USERS_SERVICE_URL = os.environ.get("USERS_SERVICE_URL", "http://users-service:5001")
ORDERS_SERVICE_URL = os.environ.get("ORDERS_SERVICE_URL", "http://orders-service:5002")

REQUEST_TIMEOUT = 5


@app.route("/")
def home():
    return jsonify(
        {
            "service": "Central Perk API Gateway ☕",
            "version": "1.0.0",
            "description": "Centralized gateway for Central Perk microservices",
            "barista": "Gunther",
            "available_endpoints": {
                "users": [
                    "GET /users - List all users",
                    "GET /users/<id> - Get user by ID",
                    "GET /users/drink/<drink> - Filter by favorite drink",
                ],
                "orders": [
                    "GET /orders - List all orders",
                    "GET /orders/<id> - Get order by ID",
                    "GET /orders/user/<user_id> - Get orders by user",
                    "GET /orders/status/<status> - Filter orders by status",
                    "GET /orders/category/<category> - Filter by category",
                ],
                "combined": [
                    "GET /users/<id>/orders - Get user with their orders",
                    "GET /dashboard - Get cafe dashboard with statistics",
                ],
                "health": ["GET /health - Health check of all services"],
            },
        }
    )


@app.route("/users", methods=["GET"])
def get_users():
    try:
        response = requests.get(
            f"{USERS_SERVICE_URL}/users", params=request.args, timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Users service unavailable", "message": str(e)}), 503


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        response = requests.get(
            f"{USERS_SERVICE_URL}/users/{user_id}", timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Users service unavailable", "message": str(e)}), 503


@app.route("/users/drink/<drink>", methods=["GET"])
def get_users_by_drink(drink):
    try:
        response = requests.get(
            f"{USERS_SERVICE_URL}/users/drink/{drink}", timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return (
            jsonify({"error": "Users service unavailable", "message": str(e)}),
            503,
        )


@app.route("/orders", methods=["GET"])
def get_orders():
    try:
        response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders", params=request.args, timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Orders service unavailable", "message": str(e)}), 503


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    try:
        response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders/{order_id}", timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Orders service unavailable", "message": str(e)}), 503


@app.route("/orders/status/<status>", methods=["GET"])
def get_orders_by_status(status):
    try:
        response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders/status/{status}", timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Orders service unavailable", "message": str(e)}), 503


@app.route("/orders/category/<category>", methods=["GET"])
def get_orders_by_category(category):
    try:
        response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders/category/{category}", timeout=REQUEST_TIMEOUT
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Orders service unavailable", "message": str(e)}), 503


@app.route("/users/<int:user_id>/orders", methods=["GET"])
def get_user_with_orders(user_id):
    try:
        user_response = requests.get(
            f"{USERS_SERVICE_URL}/users/{user_id}", timeout=REQUEST_TIMEOUT
        )

        if user_response.status_code == 404:
            return jsonify({"error": "User not found"}), 404

        user_data = user_response.json()

        orders_response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders/user/{user_id}", timeout=REQUEST_TIMEOUT
        )

        orders_data = (
            orders_response.json()
            if orders_response.status_code == 200
            else {"orders": []}
        )

        return jsonify(
            {
                "gateway": "central-perk-gateway",
                "user": user_data.get("user"),
                "orders_summary": {
                    "total_orders": orders_data.get("total_orders", 0),
                    "total_spent": orders_data.get("total_spent", 0),
                    "orders": orders_data.get("orders", []),
                },
            }
        )

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Service unavailable", "message": str(e)}), 503


@app.route("/dashboard", methods=["GET"])
def get_dashboard():
    try:
        users_response = requests.get(
            f"{USERS_SERVICE_URL}/users", timeout=REQUEST_TIMEOUT
        )

        orders_response = requests.get(
            f"{ORDERS_SERVICE_URL}/orders", timeout=REQUEST_TIMEOUT
        )

        users_data = users_response.json() if users_response.status_code == 200 else {}
        orders_data = (
            orders_response.json() if orders_response.status_code == 200 else {}
        )

        users = users_data.get("users", [])
        orders = orders_data.get("orders", [])

        active_users = len([u for u in users if u.get("active", False)])
        total_revenue = sum(o.get("price", 0) * o.get("quantity", 1) for o in orders)

        status_count = {}
        for order in orders:
            status = order.get("status", "unknown")
            status_count[status] = status_count.get(status, 0) + 1

        category_count = {}
        for order in orders:
            category = order.get("category", "unknown")
            category_count[category] = category_count.get(category, 0) + 1

        return jsonify(
            {
                "gateway": "central-perk-gateway",
                "barista": "Gunther",
                "dashboard": {
                    "users": {
                        "total": len(users),
                        "active": active_users,
                        "inactive": len(users) - active_users,
                    },
                    "orders": {
                        "total": len(orders),
                        "by_status": status_count,
                        "by_category": category_count,
                        "total_revenue": f"R$ {total_revenue:.2f}",
                    },
                    "services_status": {
                        "users_service": (
                            "online" if users_response.status_code == 200 else "offline"
                        ),
                        "orders_service": (
                            "online"
                            if orders_response.status_code == 200
                            else "offline"
                        ),
                    },
                },
            }
        )

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Services unavailable", "message": str(e)}), 503


@app.route("/health")
def health():
    services_status = {}
    overall_healthy = True

    try:
        response = requests.get(f"{USERS_SERVICE_URL}/health", timeout=2)
        services_status["users-service"] = {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
        }
    except requests.exceptions.RequestException:
        services_status["users-service"] = {"status": "unreachable"}
        overall_healthy = False

    try:
        response = requests.get(f"{ORDERS_SERVICE_URL}/health", timeout=2)
        services_status["orders-service"] = {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
        }
    except requests.exceptions.RequestException:
        services_status["orders-service"] = {"status": "unreachable"}
        overall_healthy = False

    return jsonify(
        {
            "gateway": "healthy",
            "services": services_status,
            "overall_status": "healthy" if overall_healthy else "degraded",
        }
    ), (200 if overall_healthy else 503)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
