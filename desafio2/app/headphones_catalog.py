import psycopg2
import os
import time
from datetime import datetime

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "headphones_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


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
        CREATE TABLE IF NOT EXISTS headphones (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            driver_size INTEGER,
            impedance INTEGER,
            sensitivity INTEGER,
            frequency_response VARCHAR(50),
            cable_type VARCHAR(100),
            weight INTEGER,
            price DECIMAL(10, 2),
            sound_signature VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Banco de dados inicializado: {DB_HOST}:{DB_PORT}/{DB_NAME}")


def add_headphone(
    brand,
    model,
    type_,
    driver_size,
    impedance,
    sensitivity,
    frequency_response,
    cable_type,
    weight,
    price,
    sound_signature,
    notes="",
):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO headphones (brand, model, type, driver_size, impedance, sensitivity,
                               frequency_response, cable_type, weight, price, 
                               sound_signature, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """,
        (
            brand,
            model,
            type_,
            driver_size,
            impedance,
            sensitivity,
            frequency_response,
            cable_type,
            weight,
            price,
            sound_signature,
            notes,
        ),
    )

    headphone_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Fone adicionado: {brand} {model} (ID: {headphone_id})")
    return headphone_id


def list_headphones():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM headphones ORDER BY brand, model")
    headphones = cursor.fetchall()

    column_names = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    if not headphones:
        print("\nNenhum fone encontrado no catalogo.")
        return

    print("\n" + "=" * 100)
    print("CATALOGO DE FONES DE OUVIDO AUDIOFILO")
    print("=" * 100)

    for hp in headphones:
        hp_dict = dict(zip(column_names, hp))
        print(f"\nID: {hp_dict['id']}")
        print(f"Marca/Modelo: {hp_dict['brand']} {hp_dict['model']}")
        print(f"Tipo: {hp_dict['type']}")
        print(
            f"Driver: {hp_dict['driver_size']}mm | Impedancia: {hp_dict['impedance']}ohms | Sensibilidade: {hp_dict['sensitivity']}dB"
        )
        print(f"Resposta de Frequencia: {hp_dict['frequency_response']}")
        print(f"Cabo: {hp_dict['cable_type']}")
        print(f"Peso: {hp_dict['weight']}g")
        print(f"Preco: ${float(hp_dict['price']):.2f}")
        print(f"Assinatura Sonora: {hp_dict['sound_signature']}")
        if hp_dict["notes"]:
            print(f"Notas: {hp_dict['notes']}")
        print(f"Adicionado em: {hp_dict['created_at']}")
        print("-" * 100)


def count_headphones():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM headphones")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM headphones")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(price) FROM headphones")
    avg_price = cursor.fetchone()[0] or 0

    cursor.execute(
        """
        SELECT type, COUNT(*) as count 
        FROM headphones 
        GROUP BY type 
        ORDER BY count DESC
    """
    )
    types = cursor.fetchall()

    cursor.execute(
        """
        SELECT brand, COUNT(*) as count 
        FROM headphones 
        GROUP BY brand 
        ORDER BY count DESC
    """
    )
    brands = cursor.fetchall()

    cursor.execute("SELECT AVG(impedance) FROM headphones")
    avg_impedance = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("ESTATISTICAS DO CATALOGO")
    print("=" * 80)
    print(f"Total de fones: {total}")
    print(f"Preco medio: ${float(avg_price):.2f}")
    print(f"Impedancia media: {float(avg_impedance):.0f}ohms")
    print(f"\nTipos:")
    for t in types:
        print(f"   {t[0]}: {t[1]}")
    print(f"\nMarcas:")
    for b in brands:
        print(f"   {b[0]}: {b[1]}")
    print("=" * 80)


def populate_sample_data():
    print("\nAdicionando fones de exemplo ao catalogo...")

    sample_headphones = [
        (
            "Sennheiser",
            "HD 800 S",
            "Open-back Over-ear",
            56,
            300,
            102,
            "4Hz - 51kHz",
            "Detachable 6.3mm",
            330,
            1699.99,
            "Neutral/Analytical",
            "Flagship open-back",
        ),
        (
            "Focal",
            "Clear MG",
            "Open-back Over-ear",
            40,
            55,
            104,
            "5Hz - 28kHz",
            "Detachable 3.5mm/6.3mm",
            450,
            1490.00,
            "Balanced/Slightly Warm",
            "Magnesium drivers",
        ),
        (
            "Audeze",
            "LCD-X",
            "Open-back Over-ear",
            106,
            20,
            103,
            "10Hz - 50kHz",
            "Detachable Mini-XLR",
            612,
            1199.00,
            "Neutral",
            "Planar magnetic",
        ),
        (
            "Beyerdynamic",
            "DT 1990 Pro",
            "Open-back Over-ear",
            45,
            250,
            102,
            "5Hz - 40kHz",
            "Detachable 3.5mm",
            370,
            599.00,
            "Bright/Analytical",
            "Professional studio monitoring",
        ),
        (
            "HiFiMAN",
            "Arya Stealth",
            "Open-back Over-ear",
            0,
            32,
            94,
            "8Hz - 65kHz",
            "Detachable 3.5mm",
            404,
            1299.00,
            "Neutral/Natural",
            "Stealth magnets planar",
        ),
        (
            "AKG",
            "K701",
            "Open-back Over-ear",
            44,
            62,
            105,
            "10Hz - 39.8kHz",
            "Detachable 3.5mm",
            235,
            249.00,
            "Neutral",
            "Classical music reference",
        ),
        (
            "Audio-Technica",
            "ATH-M50x",
            "Closed-back Over-ear",
            45,
            38,
            99,
            "15Hz - 28kHz",
            "Detachable 3.5mm",
            285,
            149.00,
            "V-Shaped",
            "Popular studio headphone",
        ),
        (
            "Sony",
            "MDR-Z7M2",
            "Closed-back Over-ear",
            70,
            70,
            98,
            "4Hz - 100kHz",
            "Detachable 4.4mm balanced",
            340,
            899.00,
            "Warm",
            "High-res audio 70mm drivers",
        ),
    ]

    for hp in sample_headphones:
        add_headphone(*hp)

    print("\nDados de exemplo adicionados com sucesso!")


def main():
    print("\n" + "=" * 80)
    print("SISTEMA DE CATALOGO DE FONES DE OUVIDO AUDIOFILO")
    print("=" * 80)
    print(f"Banco de dados: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    init_database()

    count = count_headphones()
    print(f"\nFones no catalogo: {count}")

    if count == 0:
        print("\nCatalogo vazio. Adicionando dados de exemplo...")
        populate_sample_data()
    else:
        print("\nDados persistidos encontrados!")

    list_headphones()

    get_statistics()

    print("\n" + "=" * 80)
    print("Sistema executado com sucesso!")
    print(f"Os dados foram salvos no PostgreSQL: {DB_HOST}/{DB_NAME}")
    print(
        "Mesmo removendo o container da aplicacao, os dados permanecerao no volume Docker"
    )
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
