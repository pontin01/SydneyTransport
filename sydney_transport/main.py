from app import App

def main():
    app = App()

    app.setup()
    app.search()

    # for connection in app.state.connections:
    #     print(connection)
    #
    # print("\n\n\n")
    # print(app.state.unvisited_stops)


if __name__ == '__main__':
    main()

"""
CREATE VIEW StopInformation AS
SELECT ST.StopID, S.StopName, S.StopLat, S.StopLon,
	   S.ParentStation, ST.TripID, ST.ArrivalTime, ST.StopSequence
  FROM StopTime ST
  	   INNER JOIN Stop S ON ST.StopID = S.StopID;
"""