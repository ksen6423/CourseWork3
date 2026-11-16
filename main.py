import psycopg2
from src.config import DB_CONFIG
from src.api import NominatimAPI, OpenSkyAPI
from src.db_utils import create_tables, insert_country, insert_aeroplanes
from src.db_manager import DBManager


def main():
    countries = ["Switzerland", "Germany", "Spain", "Canada"]

    nominatim = NominatimAPI()
    opensky = OpenSkyAPI()

    conn = psycopg2.connect(**DB_CONFIG)
    create_tables(conn)

    for country_name in countries:
        print(f"Получаем координаты для: {country_name}...")
        bbox = nominatim.get_country_bbox(country_name)
        if not bbox:
            print(f"Не удалось найти координаты для {country_name}")
            continue

        country_id = insert_country(conn, bbox)

        print(f"Запрашиваем самолеты в небе над {country_name}...")
        aeroplanes = opensky.get_aeroplanes_by_bbox(bbox)
        insert_aeroplanes(conn, aeroplanes, country_id)
        print(f"Добавлено самолетов: {len(aeroplanes)}")

    conn.close()

    db = DBManager(**DB_CONFIG)

    print("\n1. Страны и количество самолетов:")
    for row in db.get_countries_and_aeroplanes_count():
        print(row)

    print(f"\n2. Средняя скорость самолетов: {db.get_avg_speed()} м/с")

    print("\n3. Самолеты со скоростью выше средней (первые 5):")
    for row in db.get_aeroplanes_with_higher_speed()[:5]:
        print(row)

    print("\n4. Поиск по позывному 'ACA' (Air Canada):")
    for row in db.get_aeroplanes_with_keyword("ACA"):
        print(row)

    db.close()


if __name__ == "__main__":
    main()
