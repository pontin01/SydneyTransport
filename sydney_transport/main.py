from app import App

def main():
    app = App()

    app.setup()
    app.search()

    for connection in app.state.connections:
        print(connection)

    print("\n\n\n")
    print(app.state.unvisited_stops)


if __name__ == '__main__':
    main()
