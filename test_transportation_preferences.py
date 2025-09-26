import json

from preferences_manager import PreferencesManager


def test_transportation_preferences_handles_string(tmp_path):
    prefs_path = tmp_path / "prefs.json"
    prefs_data = {
        "transportation_preferences": "rideshare only",
    }
    prefs_path.write_text(json.dumps(prefs_data))

    manager = PreferencesManager(str(prefs_path))
    recommendations = manager.get_transportation_recommendations()

    assert isinstance(recommendations["ground_transport"], dict)
    assert isinstance(recommendations["car_rental"], dict)
    assert isinstance(recommendations["preferred_car_type"], str)
