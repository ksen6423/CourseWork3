import time

import requests


class NominatimAPI:  # или ваше название класса
    def get_country_bbox(self, country_name: str):
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "country": country_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "CourseWork3_AeroplanesApp/1.0"
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        time.sleep(1)

        if data:
            item = data[0]
            raw_bbox = item["boundingbox"]
            return {
                "name": country_name,  # или item["name"], если нужно официальное название из API
                "lamin": float(raw_bbox[0]),
                "lamax": float(raw_bbox[1]),
                "lomin": float(raw_bbox[2]),
                "lomax": float(raw_bbox[3]),
            }
        return None


# class NominatimAPI:
#     BASE_URL = "https://openstreetmap.org"
#
#     def get_country_bbox(self, country_name: str) -> dict | None:
#         headers = {"User-Agent": "AeroplanesTrackerStudentProject/1.0"}
#         params = {
#             "country": country_name,
#             "format": "json",
#             "limit": 1
#         }
#         response = requests.get(self.BASE_URL, params=params, headers=headers)
#         response.raise_for_status()
#         data = response.json()
#
#         # Соблюдаем политику Nominatim (не более 1 запроса в секунду)
#         time.sleep(1)
#
#         if not data:
#             return None
#
#         bbox = data[0]["boundingbox"]  # [min_lat, max_lat, min_lon, max_lon]
#         return {
#             "name": country_name,
#             "lamin": float(bbox[0]),
#             "lamax": float(bbox[1]),
#             "lomin": float(bbox[2]),
#             "lomax": float(bbox[3])
#         }
#

class OpenSkyAPI:

    def get_aeroplanes_by_bbox(self, bbox: dict) -> list[dict]:
        url = "https://opensky-network.org/api/states/all"
        params = {
            "lamin": bbox["lamin"],
            "lamax": bbox["lamax"],
            "lomin": bbox["lomin"],
            "lomax": bbox["lomax"]
        }
        headers = {
            "User-Agent": "CourseWork3_AeroplanesApp/1.0"
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        states = data.get("states") or []
        aeroplanes = []

        for state in states:
            aeroplanes.append({
                "icao24": state[0],
                "callsign": state[1].strip() if state[1] else None,
                "origin_country": state[2],
                "longitude": state[5],
                "latitude": state[6],
                "altitude": state[7],
                "on_ground": state[8],
                "velocity": state[9]
            })
        return aeroplanes
