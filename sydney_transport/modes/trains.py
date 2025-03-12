from sydney_transport.loader.stop import load_train_stations

def run_trains(db_username, db_password):
    stops = load_train_stations(db_username, db_password)
    print(stops)