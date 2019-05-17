import argparse

localhost = "127.0.0.1"


def main(args):
    pass


if __name__ == "__main__":
    description = "Go Back N Client: A reliable transport service working over UDP"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-A', '--address',
                        help='IP address of the server where the files will be sent to.',
                        default=localhost,
                        type=str)

    parser.add_argument('-F', '--file',
                        help='Path to the file to be sent.',
                        type=str)

    parser.add_argument('-W', '--window',
                        help='Integer representing size (packages number) of the window. The window size will be '
                             'constant.',
                        type=int)

    parser.add_argument('-P', '--packages',
                        help='Integer representing the size of the packages to be sent.',
                        type=int)

    parser.add_argument('-S', '--sequence',
                        help='Integer representing the maximum number of the sequence numbers.',
                        type=int)

    parser.add_argument('-I', '--in',
                        help='Integer representing the port number used to receive the ACKs.',
                        type=int)

    parser.add_argument('-O', '--out',
                        help='Integer representing the port number where the data will be sent to.',
                        type=int)

    main(parser.parse_args())
