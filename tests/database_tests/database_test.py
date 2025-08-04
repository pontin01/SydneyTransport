import pytest

import datetime

import sydney_transport.database.database as database
import sydney_transport.database.stop_db as stop_db

@pytest.fixture(scope="session", autouse=True)
def db_connection():
    """
    ...
    """
    # database connection setup
    db_username = input("Database Username: ")
    db_password = input("Database Password: ")
    conn = database.connect(db_username, db_password)

    yield conn

    # database connection teardown
    conn.close()

# ------------------------------
# TESTS
# ------------------------------

@pytest.mark.parametrize(
    "test_input, expected",
    [
        (0, 0),
        ("text", "text"),
        (True, 1)
    ]
)
def test_query(test_input, expected, db_connection):
    """
    Test the database is sending and receiving queries properly.
    """
    sql = "SELECT %s;"
    params = (test_input,)
    result = database.query(sql, params, db_connection)

    assert result[0][0] == expected

@pytest.mark.parametrize(
    "parent_station_id, expected",
    [
        (
            "G562",
            [("562", "Gungahlin College - Warwick St", -35.1852715755156, 149.128407315585, "G562")]
        ),
        (
            "2145553",
            [("2145554", "Childrens Hospital Light Rail", -33.8025900220547, 150.993004857492, "2145553"),
             ("2145576", "Childrens Hospital Light Rail", -33.8025623315004, 150.993025156642, "2145553")]
        ),
        (
            "275320",
            [("2753122", "Richmond Station - East Market St", -33.5985913002531, 150.752436212431, "275320"),
             ("2753671", "Richmond Station - Platform 1", -33.5989032173303, 150.7528482016, "275320"),
             ("2753672", "Richmond Station - Platform 2", -33.5989861783866, 150.752787184789, "275320"),
             ("275369", "East Market St Opp Richmond Station", -33.5987354477627, 150.752140926768, "275320")]
        )
    ]
)
def test_get_sibling_stop_list(parent_station_id, expected, db_connection):
    """
    Tests get_sibling_stop_list() from database/stop_db.py
    """
    result = stop_db.get_sibling_stop_list(parent_station_id, db_connection)
    assert result == expected

@pytest.mark.parametrize(
    "stop_id, arrival_time, start_day, expected",
    [
        (
            "2000345", "15:00", "Friday",
            [("623L.1352.163.64.T.8.84358624", datetime.timedelta(seconds=54480), 6)]
        ),
        (
            "2217104", "9:00", "Monday",
            [("1955670", datetime.timedelta(seconds=32880), 43),
             ("2123515", datetime.timedelta(seconds=32880), 45)]
        ),
        (
            "200817", "11:25", "Wednesday",
            [("2286708", datetime.timedelta(seconds=41340), 9),
             ("2251932", datetime.timedelta(seconds=41580), 26),
             ("2394192", datetime.timedelta(seconds=41640), 9),
             ("2357445", datetime.timedelta(seconds=41700), 13),
             ("2289886", datetime.timedelta(seconds=41820), 9),
             ("2288835", datetime.timedelta(seconds=42060), 27)]
        )
    ]
)
def test_get_trips_from_stop(stop_id, arrival_time, start_day, expected, db_connection):
    """
    Tests get_trips_from_stop() from database/stop_db.py
    """
    result = stop_db.get_trips_from_stop(stop_id, arrival_time, start_day, db_connection)
    assert result == expected

@pytest.mark.parametrize(
    "trip_id, stop_sequence, expected",
    [
        (
            "103.AB51.1-18T-1-sj2-1.2.H", 1,
            [("2142339", "Bridge St Opp Granville Station", -33.8321967998572,
              151.011658871761, "214240", datetime.timedelta(seconds=85440), 2)]
        ),
        (
            "1.AB50.1-10T-4-sj2-1.2.R", 4,
            [("2232202", "Sutherland Station - Stand A", -34.0320328947091,
              151.056683378811, "223210", datetime.timedelta(seconds=16860), 5)]
        ),
        (
            "WT28.310325.31.X.5.1415", 10,
            [("2790141", "Lithgow Station - Platform 1", -33.4805766965329,
              150.156977008511, "279010", datetime.timedelta(seconds=66000), 11)]
        )
    ]
)
def test_get_next_stop_in_trip(trip_id, stop_sequence, expected, db_connection):
    """
    Tests get_next_stop_in_trip() from database/stop_db.py
    """
    result = stop_db.get_next_stop_in_trip(trip_id, stop_sequence, db_connection)
    assert result == expected





















