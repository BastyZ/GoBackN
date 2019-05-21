import argparse
from server import Server

localhost = "127.0.0.1"


def main(args):
    server = Server(args.address, args.file, args.window, args.packages, args.sequence, args.receive, args.send)
    server.run()


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
                        default=5,  # based on examples
                        type=int)

    parser.add_argument('-P', '--packages',
                        help='Integer representing the size of the packages to be sent.',
                        default=512,  # on bytes (I hope), considering that Ethernet MTU is 1500 bytes
                        type=int)

    parser.add_argument('-S', '--sequence',
                        help='Integer representing the maximum number of the sequence numbers.',
                        default=2,  # 100 numbers seems pretty reasonable, maybe 3 after testing out
                        type=int)

    parser.add_argument('-I', '--receive',
                        help='Integer representing the port number used to receive the ACKs.',
                        default=3020,
                        type=int)

    parser.add_argument('-O', '--send',
                        help='Integer representing the port number where the data will be sent to.',
                        default=2030,  # sending them to the future (?)
                        type=int)

    main(parser.parse_args())
