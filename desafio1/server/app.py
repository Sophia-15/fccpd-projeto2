from flask import Flask, jsonify, request
from datetime import datetime
import socket
import random

app = Flask(__name__)

total_orders = 0
daily_sales = 0.0

customer_cashback = {}

MENU = {
    "Espresso": {"price": 2.50},
    "Cappuccino": {"price": 3.75},
    "Latte": {"price": 4.00},
    "Mocha": {"price": 4.50},
    "Frappuccino": {"price": 5.50},
    "Muffin": {"price": 3.00},
    "Cookie": {"price": 2.00},
    "Cheesecake": {"price": 4.75},
}

CUSTOMER_CPFS = {
    "Ross": "111.111.111-11",
    "Rachel": "222.222.222-22",
    "Monica": "333.333.333-33",
    "Chandler": "444.444.444-44",
    "Joey": "555.555.555-55",
    "Phoebe": "666.666.666-66",
}


def get_random_item():
    return random.choice(list(MENU.keys()))


def get_random_customer():
    return random.choice(list(CUSTOMER_CPFS.keys()))


def calculate_cashback(price):
    return round(price * 0.01, 2)


def get_customer_cashback(cpf):
    return customer_cashback.get(cpf, 0.0)


def add_cashback(cpf, amount):
    if cpf not in customer_cashback:
        customer_cashback[cpf] = 0.0
    customer_cashback[cpf] += amount
    customer_cashback[cpf] = round(customer_cashback[cpf], 2)


@app.route("/")
def home():
    global total_orders, daily_sales

    total_orders += 1

    item_name = get_random_item()
    item_data = MENU[item_name]
    customer_name = get_random_customer()
    customer_cpf = CUSTOMER_CPFS[customer_name]

    cashback_earned = calculate_cashback(item_data["price"])
    add_cashback(customer_cpf, cashback_earned)

    daily_sales += item_data["price"]

    client_ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()

    response_data = {
        "order": {
            "number": total_orders,
            "item": f"{item_name}",
            "price": f"${item_data['price']:.2f}",
            "status": "confirmed",
        },
        "customer": {
            "name": customer_name,
            "cpf": customer_cpf,
            "cashback_earned": f"${cashback_earned:.2f}",
            "cashback_balance": f"${get_customer_cashback(customer_cpf):.2f}",
        },
        "server_info": {
            "barista": "Gunther",
            "container": hostname,
            "client_ip": client_ip,
            "timestamp": timestamp,
        },
    }

    log_msg = f"[{timestamp}] Pedido #{total_orders} | {customer_name} | {item_name} (${item_data['price']:.2f}) | Cashback: +${cashback_earned:.2f}"
    print(log_msg)

    return jsonify(response_data), 200


@app.route("/health")
def health():
    return (
        jsonify(
            {
                "status": "open",
                "cafeteria": "Central Perk",
                "barista": "Gunther",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ),
        200,
    )


@app.route("/stats")
def stats():
    total_cashback = sum(customer_cashback.values())

    return (
        jsonify(
            {
                "cafeteria": {
                    "total_orders": total_orders,
                    "daily_sales": f"${daily_sales:.2f}",
                    "average_order": (
                        f"${(daily_sales / total_orders):.2f}"
                        if total_orders > 0
                        else "$0.00"
                    ),
                    "total_cashback_distributed": f"${total_cashback:.2f}",
                    "status": "open",
                },
                "customers": {
                    name: {
                        "cpf": cpf,
                        "cashback_balance": f"${get_customer_cashback(cpf):.2f}",
                    }
                    for name, cpf in CUSTOMER_CPFS.items()
                },
                "server": {
                    "barista": "Gunther",
                    "container": socket.gethostname(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
        ),
        200,
    )


@app.route("/menu")
def menu():
    menu_formatted = {}
    for item, data in MENU.items():
        menu_formatted[item] = {
            "name": f"{item}",
            "price": f"${data['price']:.2f}",
            "cashback": f"${calculate_cashback(data['price']):.2f} (1%)",
        }

    return (
        jsonify(
            {
                "menu": menu_formatted,
                "cashback_info": "Ganhe 1% de cashback em cada compra, vinculado ao seu CPF!",
                "location": "New York, NY",
            }
        ),
        200,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("CENTRAL PERK CAFETERIA")
    print("=" * 60)
    print("New York, NY - Greenwich Village")
    print("Barista: Gunther")
    print("Programa de Cashback: 1% em todas as compras")
    print("Cashback vinculado ao CPF do cliente")
    print("=" * 60)
    print("Cafeteria aberta na porta 8080...")
    print("=" * 60)
    print()
    app.run(host="0.0.0.0", port=8080, debug=False)
