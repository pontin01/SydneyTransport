from ..database import connect
from ..classes.stop import Stop

def load_train_stations(username, password):
    sydtp_db = connect(username, password)
    cursor = sydtp_db.cursor()

    sql = """SELECT StopID, StopName, StopLat, StopLon
    FROM Stop 
    WHERE StopName LIKE '%Station%'
          AND StopCode IS NULL
          AND LocationType IS NOT NULL
          AND ParentStation IS NULL
          AND StopID LIKE '2%'
          AND StopName NOT LIKE '%Historic%'"""

    cursor.execute(sql)
    result = cursor.fetchall()

    stop_ls = []

    for x in result:
        stop = Stop(stop_id=x[0], stop_code=None, stop_name=x[1], stop_lat=x[2],
                    stop_lon=x[3], location_type=None, parent_station=None,
                    wheelchair_boarding=None, level_id=None, platform_code=None)
        stop_ls.append(stop)

    return stop_ls