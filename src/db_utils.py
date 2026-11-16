def create_tables(conn) -> None:
    """Функция для создания таблиц."""
    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE IF EXISTS aeroplanes;
            DROP TABLE IF EXISTS countries;

            CREATE TABLE countries (
                country_id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                lamin FLOAT NOT NULL,
                lamax FLOAT NOT NULL,
                lomin FLOAT NOT NULL,
                lomax FLOAT NOT NULL
            );

            CREATE TABLE aeroplanes (
                aeroplane_id SERIAL PRIMARY KEY,
                icao24 VARCHAR(20) NOT NULL,
                callsign VARCHAR(20),
                origin_country VARCHAR(100),
                longitude FLOAT,
                latitude FLOAT,
                altitude FLOAT,
                on_ground BOOLEAN,
                velocity FLOAT,
                country_id INT REFERENCES countries(country_id) ON DELETE CASCADE
            );
        """)
    conn.commit()


def insert_country(conn, country_data: dict) -> int:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO countries (name, lamin, lamax, lomin, lomax)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING country_id;
        """, (
            country_data["name"],
            country_data["lamin"],
            country_data["lamax"],
            country_data["lomin"],
            country_data["lomax"]
        ))
        country_id = cur.fetchone()[0]
    conn.commit()
    return country_id


def insert_aeroplanes(conn, aeroplanes: list[dict], country_id: int) -> None:
    if not aeroplanes:
        return

    with conn.cursor() as cur:
        for plane in aeroplanes:
            cur.execute("""
                INSERT INTO aeroplanes (
                    icao24, callsign, origin_country, longitude,
                    latitude, altitude, on_ground, velocity, country_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                plane["icao24"],
                plane["callsign"],
                plane["origin_country"],
                plane["longitude"],
                plane["latitude"],
                plane["altitude"],
                plane["on_ground"],
                plane["velocity"],
                country_id
            ))
    conn.commit()
