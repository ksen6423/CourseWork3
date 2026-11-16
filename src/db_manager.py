import psycopg2


class DBManager:
    """Класс для работы с данными в БД."""
    def __init__(self, database, user, password, host, port):
        self.conn = psycopg2.connect(
            database=database, user=user, password=password, host=host, port=port
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def add_country(self, name, country_code):
        try:
            self.cur.execute(
                "INSERT INTO countries (name, country_code) VALUES (%s, %s) ON CONFLICT (country_code) DO NOTHING",
                (name, country_code)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error adding country: {e}")

    def add_aeroplane(self, icao24, callsign, origin_country, latitude, longitude, velocity, last_contact):
        try:
            self.cur.execute(
                """
                INSERT INTO aeroplanes (icao24, callsign, origin_country, latitude, longitude, velocity, last_contact)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (icao24) DO UPDATE SET
                    callsign = EXCLUDED.callsign,
                    origin_country = EXCLUDED.origin_country,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    velocity = EXCLUDED.velocity,
                    last_contact = EXCLUDED.last_contact
                """,
                (icao24, callsign, origin_country, latitude, longitude, velocity, last_contact)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error adding aeroplane: {e}")

    def get_countries_and_aeroplanes_count(self) -> list[tuple]:
        """Получает список всех стран и количество самолетов в их воздушных пространствах."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, COUNT(a.aeroplane_id)
                FROM countries c
                LEFT JOIN aeroplanes a ON c.country_id = a.country_id
                GROUP BY c.name
                ORDER BY COUNT(a.aeroplane_id) DESC;
            """)
            return cur.fetchall()

    def get_all_aeroplanes(self) -> list[tuple]:
        """Получает список всех воздушных судов."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT a.icao24, a.callsign, a.origin_country, a.velocity, a.altitude, c.name
                FROM aeroplanes a
                JOIN countries c ON a.country_id = c.country_id;
            """)
            return cur.fetchall()

    def get_avg_speed(self) -> float:
        """Получает среднюю скорость по самолетам."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT ROUND(AVG(velocity)::numeric, 2)
                FROM aeroplanes
                WHERE velocity IS NOT NULL;
            """)
            result = cur.fetchone()[0]
            return float(result) if result else 0.0

    def get_aeroplanes_with_higher_speed(self) -> list[tuple]:
        """Получает список всех самолетов, у которых скорость выше средней."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT icao24, callsign, origin_country, velocity
                FROM aeroplanes
                WHERE velocity > (SELECT AVG(velocity) FROM aeroplanes WHERE velocity IS NOT NULL)
                ORDER BY velocity DESC;
            """)
            return cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword: str) -> list[tuple]:
        """Получает список всех самолетов, в позывном которых содержатся переданные символы."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT icao24, callsign, origin_country, velocity
                FROM aeroplanes
                WHERE callsign ILIKE %s;
            """, (f"%{keyword}%",))
            return cur.fetchall()

    def close(self) -> None:
        self.conn.close()
