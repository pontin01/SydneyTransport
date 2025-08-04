from sydney_transport.database.database import query

def get_sibling_stop_list(parent_station_id: str, db_connection) -> list[tuple]:
    """
    Gets a list of sibling stops from the database.
    """
    sql = """
        SELECT StopID, StopName, StopLat, StopLon, ParentStation
          FROM Stop
         WHERE ParentStation = %s
               AND LocationType IS NULL;
    """
    params = (parent_station_id,)

    return query(sql, params, db_connection)

def get_trips_from_stop(stop_id, arrival_time, start_day, db_connection) -> list[tuple]:
    """
    Gets a list of Trips associated with a Stop from the database.
    """
    sql = f"""
        WITH RankedDepartures AS (
            SELECT ST.StopID, T.DirectionID, T.TripID, ST.StopSequence,
                   ST.ArrivalTime, R.RouteID,
                   ROW_NUMBER() OVER (
                       PARTITION BY ST.StopID, T.DirectionID, R.RouteID
                       ORDER BY ST.ArrivalTime ASC
                   ) AS RowNumber
              FROM StopTime ST
                   INNER JOIN Trip T ON ST.TripID = T.TripID
                   INNER JOIN Route R ON T.RouteID = R.RouteID
                   INNER JOIN Service S ON T.ServiceID = S.ServiceID
             WHERE ST.StopID = %s
                   AND ST.ArrivalTime > %s
                   AND S.{start_day} = 1
        )
          SELECT TripID, ArrivalTime, StopSequence
            FROM RankedDepartures
           WHERE RowNumber = 1
                 AND ArrivalTime <= ADDTIME(%s, "00:30:00")
        ORDER BY ArrivalTime ASC;
    """
    params = (stop_id, arrival_time, arrival_time)

    return query(sql, params, db_connection)

def get_all_following_stops_in_trip(trip_id, stop_sequence, db_connection) -> list[tuple]:
    """
    Gets all information about the next stops within a Trip.
    """
    sql = """
        SELECT StopID, StopName, StopLat, StopLon, ParentStation,
               ArrivalTime, StopSequence
          FROM StopInformation
         WHERE TripID = %s
               AND StopSequence > %s;
    """
    params = (trip_id, stop_sequence)

    return query(sql, params, db_connection)

def get_stop_information_from_name(stop_name: str, db_connection) -> list[tuple]:
    """
    Gets a Stops information based on its name.
    """
    sql = """
        SELECT StopID, StopLat, StopLon, ParentStation
          FROM Stop
         WHERE StopName = %s;
    """
    params = (stop_name,)

    return query(sql, params, db_connection)

























