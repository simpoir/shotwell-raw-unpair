#!/usr/bin/env python3
"""Uncouple removed RAW files from JPG."""

import argparse
import logging
import os
import sqlite3

from xdg.BaseDirectory import xdg_data_home

DEFAULT_DB = os.path.join(xdg_data_home, "shotwell", "data", "photo.db")
RAW_EXT = "NEF"


def _make_parser():
    parser = argparse.ArgumentParser(
        description=__doc__)
    parser.add_argument("path", nargs="+",
                        help="Uncouple only RAW files matching this path")
    parser.add_argument("-d", "--debug", action="store_const",
                        const=logging.DEBUG, default=logging.INFO,
                        help="Show debug info")
    parser.add_argument("--dry-run",
                        default=False, action="store_true",
                        help="Don't do anything, just simulate.")
    return parser


def _switch_to_backing(cursor, photo_id, filepath):
    """Replace file path with path from backing file."""
    query = ("UPDATE PhotoTable"
             " SET filename = ?, develop_camera_id = -1 WHERE id = ?")
    params = (filepath, photo_id)
    cursor.execute(query, params)
    logging.debug(" Switched to backing file.")


def _remove_backing(cursor, backing_id):
    """Remove backing file."""
    query = "DELETE FROM BackingPhotoTable WHERE id = ?"
    params = (backing_id,)
    cursor.execute(query, params)
    logging.debug(" Removed backing file.")


def _unpair(cursor, photo_id, backing_id):
    """Replace raw photo path by its backing file."""
    query = "SELECT filepath FROM BackingPhotoTable WHERE id = ?"
    params = (backing_id,)
    for filepath, in cursor.execute(query, params).fetchall():
        logging.debug("candidate backing file: %s", filepath)
        if filepath.endswith("JPG") and os.path.exists(filepath):
            logging.info("Found a valid exiting backing file: %s", filepath)
            _switch_to_backing(cursor, photo_id, filepath)
            _remove_backing(cursor, backing_id)
            break
    logging.info("Could not find backing photo.")


def _query(cursor, path):
    """Look for backing file and do the swap."""
    query = (
        "SELECT id, develop_camera_id, filename"
        " FROM PhotoTable WHERE filename LIKE ?")
    params = ("{}%.{}".format(path, RAW_EXT),)
    for photo_id, backing_id, filename in cursor.execute(query,
                                                         params).fetchall():
        if not os.path.exists(filename):
            logging.info("Found missing photo: %s", filename)
            _unpair(cursor, photo_id, backing_id)



def main():
    """Run the script."""
    args = _make_parser().parse_args()
    logging.basicConfig(level=args.debug)
    connection = sqlite3.connect(DEFAULT_DB, isolation_level="DEFERRED")
    cursor = connection.cursor()
    for path in args.path:
        logging.debug("scanning path %s", path)
        _query(cursor, path)

    if args.dry_run:
        connection.rollback()
    else:
        connection.commit()


if __name__ == "__main__":
    main()
