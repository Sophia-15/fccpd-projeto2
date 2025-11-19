import psycopg2
import os
import sys
import time

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


def read_catalog():
    print("\n" + "=" * 80)
    print("LENDO CATALOGO DE FONES DE OUVIDO (CONTAINER LEITOR)")
    print("=" * 80)
    print(f"Conectando a: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'headphones'
        """
        )

        if not cursor.fetchone():
            print("\nTabela 'headphones' nao encontrada!")
            print("Execute o container principal primeiro para criar os dados.")
            cursor.close()
            conn.close()
            return

        cursor.execute("SELECT COUNT(*) FROM headphones")
        total = cursor.fetchone()[0]

        print(f"\nTotal de fones encontrados: {total}")

        if total == 0:
            print("\nCatalogo vazio.")
            cursor.close()
            conn.close()
            return

        cursor.execute("SELECT * FROM headphones ORDER BY brand, model")
        headphones = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]

        print("\n" + "=" * 80)
        print("LISTA DE FONES PERSISTIDOS")
        print("=" * 80)

        for hp in headphones:
            hp_dict = dict(zip(column_names, hp))
            print(f"\n{hp_dict['id']:02d} | {hp_dict['brand']} {hp_dict['model']}")
            print(f"   {hp_dict['type']}")
            print(
                f"   {hp_dict['driver_size']}mm | {hp_dict['impedance']}ohms | {hp_dict['sensitivity']}dB"
            )
            print(f"   ${float(hp_dict['price']):.2f} | {hp_dict['sound_signature']}")

        cursor.execute("SELECT AVG(price) FROM headphones")
        avg_price = cursor.fetchone()[0]

        cursor.execute("SELECT MIN(price) FROM headphones")
        min_price = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(price) FROM headphones")
        max_price = cursor.fetchone()[0]

        print("\n" + "=" * 80)
        print("RESUMO ESTATISTICO")
        print("=" * 80)
        print(f"Preco medio: ${float(avg_price):.2f}")
        print(f"Mais barato: ${float(min_price):.2f}")
        print(f"Mais caro: ${float(max_price):.2f}")
        print("=" * 80)

        cursor.close()
        conn.close()

        print("\nDados lidos com sucesso do banco persistente!")
        print("Estes dados sobrevivem a remocao dos containers da aplicacao")
        print("=" * 80 + "\n")

    except psycopg2.Error as e:
        print(f"\nErro ao acessar o banco de dados: {e}")
        sys.exit(1)


if __name__ == "__main__":
    read_catalog()
