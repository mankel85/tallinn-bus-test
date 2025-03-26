def find_oilme_stops_and_routes():
    return {
        "oilme_stop_ids": ["1356", "1357"],
        "routes_with_oilme": ["3", "16", "28", "39", "73"]
    }

def get_schedule_for_route(route_id):
    # Dummy example times
    return [
        {"time": "08:00", "headsign": "Keskuse"},
        {"time": "08:30", "headsign": "Kesklinn"},
        {"time": "09:00", "headsign": "Balti jaam"},
    ]