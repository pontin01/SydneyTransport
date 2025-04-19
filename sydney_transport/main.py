import sys

from database import connect
from sydney_transport.objects.stop import Stop
from sydney_transport.objects.path import Path
from sydney_transport.search_state import SearchState

def main(args):
    state = SearchState()

    # get and store search information
    try:
        state.db_username = input("Database Username: ")
        state.db_password = input("Database Password: ")
        start_stop_name = input("Start Stop Name: ")
        end_stop_name = input("End Stop Name: ")
        state.desired_day = get_desired_day()
        state.desired_time = input("Time you want to Arrive/Depart: ")
        state.search_method = input("Would you like to Arrive or Depart at this time? ")
    except EOFError:
        sys.exit(0)

    # get start stop information
    start_stop = stop_name_to_info(state, start_stop_name)
    state.start_id = start_stop.stop_id
    state.searched_stops[start_stop.stop_id] = start_stop

    # get end stop information
    end_stop = stop_name_to_info(state, end_stop_name)
    state.end_id = end_stop.stop_id

    new_paths = create_path(state, start_stop)
    for path in new_paths:
        find_path_stops(state, path)







def get_desired_day():
    while True:
        desired_day = input("Day you want the trip to be on: ")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
                "sunday"]
        if desired_day.lower() not in days:
            print("Enter a valid day of the week")
            continue
        break

    return desired_day


def stop_name_to_info(state: SearchState, stop_name: str = None):
    sql = """SELECT StopID, StopLat, StopLon, ParentStation
             FROM Stop
             WHERE StopName = %s;"""

    with connect(state.db_username, state.db_password) as sydtp_db:
        with sydtp_db.cursor() as cursor:
            print(f"sql: \n {sql} \n\n {stop_name = }")

            params = (stop_name,)
            cursor.execute(sql, params)
            result = cursor.fetchall()[0]

            print(result)

    return Stop(result[0], stop_name, result[1], result[2], result[3])


def create_path(state: SearchState, stop: Stop):
    sql = f"""(SELECT T.TripID, RouteID, DirectionID, StopSequence, ArrivalTime
                FROM StopTime ST INNER JOIN Trip T ON (ST.TripID = T.TripID)
                     INNER JOIN Service S ON (T.ServiceID = S.ServiceID)
               WHERE ST.StopID = %s
	                 AND ST.DepartureTime > %s
	                 AND S.{state.desired_day} = 1
	                 AND T.DirectionID = 0
            ORDER BY ST.DepartureTime ASC
               LIMIT 1)
        UNION
             (SELECT T.TripID, RouteID, DirectionID, StopSequence, ArrivalTime
                FROM StopTime ST INNER JOIN Trip T ON (ST.TripID = T.TripID)
                     INNER JOIN Service S ON (T.ServiceID = S.ServiceID)
               WHERE ST.StopID = %s
	                 AND ST.DepartureTime > %s
	                 AND S.{state.desired_day} = 1
	                 AND T.DirectionID = 1
            ORDER BY ST.DepartureTime ASC
               LIMIT 1);"""
    print(sql)

    with connect(state.db_username, state.db_password) as sydtp_db:
        with sydtp_db.cursor() as cursor:
            params = (stop.stop_id, state.desired_time, stop.stop_id, state.desired_time)
            cursor.execute(sql, params)
            result = cursor.fetchall()

    new_path_ls = []

    for path in result:
        trip_id = path[0]
        route_id = path[1]
        direction_id = path[2]
        stop_sequence = path[3]
        arrival_time = path[4]

        new_path = Path(trip_id, route_id, direction_id)
        new_path.add_stop(stop, stop_sequence, arrival_time)
        state.searched_paths[trip_id] = new_path
        new_path_ls.append(new_path)

    return new_path_ls

def find_path_stops(state: SearchState, path: Path):
    sql = """SELECT S.StopID, StopName, StopLat, StopLon, ParentStation,
                    StopSequence, ArrivalTime
    FROM StopTime ST INNER JOIN Stop S ON (S.StopID = ST.StopID)
    WHERE ST.TripID = %s
	      AND ST.StopSequence > %s;"""
    print(f"{path.trip_id = }")
    print(f"{path.stops[0][0]}")

    with connect(state.db_username, state.db_password) as sydtp_db:
        with sydtp_db.cursor() as cursor:
            # provide params trip_id and stop sequence
            params = (path.trip_id, path.stops[0][0])
            cursor.execute(sql, params)
            result = cursor.fetchall()

    print(result)
    print(f"{state.end_id = }")

    for stop_record in result:
        stop_id = stop_record[0]
        stop_name = stop_record[1]
        stop_lat = stop_record[2]
        stop_lon = stop_record[3]
        parent_station = stop_record[4]
        stop_sequence = stop_record[5]
        arrival_time = stop_record[6]

        temp_stop = Stop(stop_id, stop_name, stop_lat, stop_lon, parent_station)
        path.add_stop(temp_stop, stop_sequence, arrival_time)
        state.searched_paths[stop_id] = temp_stop

        if stop_id == state.end_id:
            finish()
            break

    path.print_stops()


def finish():
    print("Done!")

if __name__ == "__main__":
    main(sys.argv)