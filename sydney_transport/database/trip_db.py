from sydney_transport.database.database import query

def get_trip_info_after_search(trip_id: str, db_connection) -> list[tuple]:
    """
    Finds the RouteShortName, RouteLongName, RouteDesc, and RouteColour using the TripID.
    """
    sql = """
        SELECT R.RouteShortName, R.RouteLongName, R.RouteDesc, R.RouteColour
          FROM Trip T 
  	           INNER JOIN Route R ON T.RouteID = R.RouteID
         WHERE T.TripID = %s;
    """
    params = (trip_id,)

    return query(sql, params, db_connection)
