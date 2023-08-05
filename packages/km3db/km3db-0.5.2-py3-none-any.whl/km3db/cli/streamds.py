#!/usr/bin/env python3
"""
Access the KM3NeT StreamDS DataBase service.

Usage:
    streamds
    streamds list
    streamds info STREAM
    streamds get [-f FORMAT] STREAM [PARAMETERS...]
    streamds (-h | --help)
    streamds --version

Options:
    STREAM      Name of the stream.
    PARAMETERS  List of parameters separated by space (e.g. detid=29).
    -f FORMAT   Usually 'txt' for ASCII or 'text' for UTF-8 [default: txt].
    -x          Do not verify the SSL certificate.
    -h --help   Show this screen.

"""
import logging

import km3db
from docopt import docopt


log = logging.getLogger("streamds")

RUNSUMMARY_URL = "https://km3netdbweb.in2p3.fr/jsonds/runsummarynumbers/i"
REQUIRED_COLUMNS = set(["run", "det_id", "source"])


def print_streams():
    """Print all available streams with their full description"""
    sds = km3db.StreamDS()
    sds.print_streams()


def print_info(stream):
    """Print the information about a stream"""
    sds = km3db.StreamDS()
    sds.help(stream)


def get_data(stream, parameters, fmt):
    """Retrieve data for given stream and parameters, or None if not found"""
    sds = km3db.StreamDS()
    if stream not in sds.streams:
        log.error("Stream '{}' not found in the database.".format(stream))
        return
    params = {}
    if parameters:
        for parameter in parameters:
            if "=" not in parameter:
                log.error(
                    "Invalid parameter syntax '{}'\n"
                    "The correct syntax is 'parameter=value'".format(parameter)
                )
                continue
            key, value = parameter.split("=")
            params[key] = value
    data = sds.get(stream, fmt, **params)
    if data is not None:
        try:
            print(data)
        except BrokenPipeError:
            pass
    else:
        sds.help(stream)


def available_streams():
    """Show a short list of available streams."""
    sds = km3db.StreamDS()
    print("Available streams: ")
    print(", ".join(sorted(sds.streams)))


def main():
    args = docopt(__doc__)

    if args["info"]:
        print_info(args["STREAM"])
    elif args["list"]:
        print_streams()
    elif args["get"]:
        get_data(args["STREAM"], args["PARAMETERS"], fmt=args["-f"])
    else:
        available_streams()
