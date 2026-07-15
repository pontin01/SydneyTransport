import sys

from utils import extract_cmd_line_options

def main(args: list) -> None:
    search_options = extract_cmd_line_options(args)



if __name__ == "__main__":
    main(sys.argv)
