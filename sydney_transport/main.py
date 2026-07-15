import sys

from sydney_transport.utils import retrieve_settings
from sydney_transport.search_components.search2 import Search

def main(args: list) -> None:
    user_settings, search_settings = retrieve_settings(args)

    search = Search()


if __name__ == "__main__":
    main(sys.argv)
