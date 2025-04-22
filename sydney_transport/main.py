from datetime import datetime, timedelta

from app import App
from sydney_transport.stop import Stop
from sydney_transport.binary_tree.avl_tree import AvlTree
from sydney_transport.binary_tree.node import Node

def main():
    app = App()

    app.setup()
    app.search()

    # for connection in app.state.connections:
    #     print(connection)

    # print("\n\n\n")
    # print(app.state.unvisited_stops)

    # nodes = []
    # for i in range(1, 11):
    #     stop = Stop(
    #         str(i),
    #         f"test{i}",
    #         0.1,
    #         0.1,
    #         str(i),
    #         str(i),
    #         datetime.strptime("15:00", "%H:%M"),
    #         i
    #     )
    #     nodes.append([stop, timedelta(minutes=i)])
    #
    #
    # bt = AvlTree(Node(nodes[0][0], nodes[0][1]))
    # for node in nodes:
    #     bt.insert(node[0], node[1])


if __name__ == '__main__':
    main()

"""
CREATE VIEW StopInformation AS
SELECT ST.StopID, S.StopName, S.StopLat, S.StopLon,
	   S.ParentStation, ST.TripID, ST.ArrivalTime, ST.StopSequence
  FROM StopTime ST
  	   INNER JOIN Stop S ON ST.StopID = S.StopID;
"""