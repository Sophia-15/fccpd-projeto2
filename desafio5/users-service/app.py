from flask import Flask, jsonify, request
import os

app = Flask(__name__)

USERS_DB = {
    1: {
        "id": 1,
        "name": "Ana Clara Gomes",
        "email": "ana.gomes@centralperk.com",
        "cpf": "123.456.789-01",
        "member_since": "2023-06-10",
        "favorite_drink": "Cappuccino",
        "loyalty_points": 150,
        "active": True,
    },
    2: {
        "id": 2,
        "name": "Gabriel Albuquerque",
        "email": "gabriel.albuquerque@centralperk.com",
        "cpf": "234.567.890-12",
        "member_since": "2023-08-22",
        "favorite_drink": "Espresso",
        "loyalty_points": 220,
        "active": True,
    },
    3: {
        "id": 3,
        "name": "Paulo Rosado",
        "email": "paulo.rosado@centralperk.com",
        "cpf": "345.678.901-23",
        "member_since": "2024-01-15",
        "favorite_drink": "Latte",
        "loyalty_points": 95,
        "active": True,
    },
    4: {
        "id": 4,
        "name": "Gustavo Mourato",
        "email": "gustavo.mourato@centralperk.com",
        "cpf": "456.789.012-34",
        "member_since": "2024-03-08",
        "favorite_drink": "Mocha",
        "loyalty_points": 180,
        "active": True,
    },
    5: {
        "id": 5,
        "name": "Vinícius de Andrade",
        "email": "vinicius.andrade@centralperk.com",
        "cpf": "567.890.123-45",
        "member_since": "2024-05-20",
        "favorite_drink": "Americano",
        "loyalty_points": 65,
        "active": True,
    },
    6: {
        "id": 6,
        "name": "Luan Kato",
        "email": "luan.kato@centralperk.com",
        "cpf": "678.901.234-56",
        "member_since": "2023-11-03",
        "favorite_drink": "Macchiato",
        "loyalty_points": 310,
        "active": True,
    },
}


@app.route("/")
def home():
    return jsonify(
        {
            "service": "Central Perk - Users Service ☕",
            "version": "1.0.0",
            "endpoints": [
                "GET /users - List all users",
                "GET /users/<id> - Get user by ID",
                "GET /users/drink/<drink> - Filter users by favorite drink",
                "GET /health - Health check",
            ],
        }
    )


@app.route("/users", methods=["GET"])
def get_users():
    active_filter = request.args.get("active")

    users = list(USERS_DB.values())

    if active_filter is not None:
        active_bool = active_filter.lower() == "true"
        users = [u for u in users if u["active"] == active_bool]

    return jsonify({"service": "users-service", "total": len(users), "users": users})


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = USERS_DB.get(user_id)

    if not user:
        return (
            jsonify({"service": "users-service", "error": "User not found"}),
            404,
        )

    return jsonify({"service": "users-service", "user": user})


@app.route("/users/drink/<drink>", methods=["GET"])
def get_users_by_drink(drink):
    users = [
        u for u in USERS_DB.values() if u["favorite_drink"].lower() == drink.lower()
    ]

    return jsonify(
        {
            "service": "users-service",
            "favorite_drink": drink,
            "total": len(users),
            "users": users,
        }
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "service": "users-service",
            "total_users": len(USERS_DB),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
