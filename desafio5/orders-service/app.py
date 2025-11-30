from flask import Flask, jsonify, request
import os

app = Flask(__name__)

ORDERS_DB = {
    1: {
        "id": 1,
        "user_id": 1,
        "user_name": "Ana Clara Gomes",
        "product": "Cappuccino Grande",
        "category": "Bebida Quente",
        "quantity": 2,
        "price": 12.50,
        "status": "delivered",
        "order_date": "2024-11-28 08:30",
        "served_by": "Gunther",
    },
    2: {
        "id": 2,
        "user_id": 2,
        "user_name": "Gabriel Albuquerque",
        "product": "Espresso Duplo",
        "category": "Bebida Quente",
        "quantity": 1,
        "price": 8.00,
        "status": "delivered",
        "order_date": "2024-11-28 09:15",
        "served_by": "Gunther",
    },
    3: {
        "id": 3,
        "user_id": 3,
        "user_name": "Paulo Rosado",
        "product": "Latte com Caramelo",
        "category": "Bebida Quente",
        "quantity": 1,
        "price": 14.00,
        "status": "ready",
        "order_date": "2024-11-30 10:00",
        "served_by": "Gunther",
    },
    4: {
        "id": 4,
        "user_id": 1,
        "user_name": "Ana Clara Gomes",
        "product": "Cheesecake de Frutas Vermelhas",
        "category": "Sobremesa",
        "quantity": 1,
        "price": 18.00,
        "status": "delivered",
        "order_date": "2024-11-29 14:30",
        "served_by": "Gunther",
    },
    5: {
        "id": 5,
        "user_id": 4,
        "user_name": "Gustavo Mourato",
        "product": "Mocha com Chantilly",
        "category": "Bebida Quente",
        "quantity": 2,
        "price": 15.50,
        "status": "preparing",
        "order_date": "2024-11-30 11:20",
        "served_by": "Gunther",
    },
    6: {
        "id": 6,
        "user_id": 5,
        "user_name": "Vinícius de Andrade",
        "product": "Americano",
        "category": "Bebida Quente",
        "quantity": 1,
        "price": 9.00,
        "status": "delivered",
        "order_date": "2024-11-29 16:45",
        "served_by": "Gunther",
    },
    7: {
        "id": 7,
        "user_id": 6,
        "user_name": "Luan Kato",
        "product": "Macchiato",
        "category": "Bebida Quente",
        "quantity": 1,
        "price": 11.00,
        "status": "ready",
        "order_date": "2024-11-30 12:00",
        "served_by": "Gunther",
    },
    8: {
        "id": 8,
        "user_id": 2,
        "user_name": "Gabriel Albuquerque",
        "product": "Croissant de Chocolate",
        "category": "Doce",
        "quantity": 2,
        "price": 8.50,
        "status": "delivered",
        "order_date": "2024-11-29 09:30",
        "served_by": "Gunther",
    },
    9: {
        "id": 9,
        "user_id": 3,
        "user_name": "Paulo Rosado",
        "product": "Brownie de Chocolate",
        "category": "Doce",
        "quantity": 1,
        "price": 12.00,
        "status": "delivered",
        "order_date": "2024-11-28 15:00",
        "served_by": "Gunther",
    },
    10: {
        "id": 10,
        "user_id": 4,
        "user_name": "Gustavo Mourato",
        "product": "Frappuccino de Caramelo",
        "category": "Bebida Gelada",
        "quantity": 1,
        "price": 16.00,
        "status": "preparing",
        "order_date": "2024-11-30 13:15",
        "served_by": "Gunther",
    },
}


@app.route("/")
def home():
    return jsonify(
        {
            "service": "Central Perk - Orders Service ☕",
            "version": "1.0.0",
            "endpoints": [
                "GET /orders - List all orders",
                "GET /orders/<id> - Get order by ID",
                "GET /orders/user/<user_id> - Get orders by user",
                "GET /orders/status/<status> - Filter orders by status",
                "GET /orders/category/<category> - Filter orders by category",
                "GET /health - Health check",
            ],
        }
    )


@app.route("/orders", methods=["GET"])
def get_orders():
    status_filter = request.args.get("status")

    orders = list(ORDERS_DB.values())

    if status_filter:
        orders = [o for o in orders if o["status"].lower() == status_filter.lower()]

    return jsonify(
        {"service": "orders-service", "total": len(orders), "orders": orders}
    )


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = ORDERS_DB.get(order_id)

    if not order:
        return jsonify({"service": "orders-service", "error": "Order not found"}), 404

    return jsonify({"service": "orders-service", "order": order})


@app.route("/orders/user/<int:user_id>", methods=["GET"])
def get_orders_by_user(user_id):
    orders = [o for o in ORDERS_DB.values() if o["user_id"] == user_id]

    total_value = sum(o["price"] * o["quantity"] for o in orders)

    return jsonify(
        {
            "service": "orders-service",
            "user_id": user_id,
            "user_name": orders[0]["user_name"] if orders else "Unknown",
            "total_orders": len(orders),
            "total_spent": total_value,
            "orders": orders,
        }
    )


@app.route("/orders/status/<status>", methods=["GET"])
def get_orders_by_status(status):
    orders = [o for o in ORDERS_DB.values() if o["status"].lower() == status.lower()]

    return jsonify(
        {
            "service": "orders-service",
            "status": status,
            "total": len(orders),
            "orders": orders,
        }
    )


@app.route("/orders/category/<category>", methods=["GET"])
def get_orders_by_category(category):
    orders = [
        o for o in ORDERS_DB.values() if o["category"].lower() == category.lower()
    ]

    return jsonify(
        {
            "service": "orders-service",
            "category": category,
            "total": len(orders),
            "orders": orders,
        }
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "service": "orders-service",
            "total_orders": len(ORDERS_DB),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)
