#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alexandre Boucaud <aboucaud@lal.in2p3.fr>

import gzip
import pickle

from pathlib import Path
from collections import defaultdict

from astropy.table import Table

LSST_FILTERS = 'ugrizY'


def parse_lsst_phot_table(table, rows):
    """
    Retrieve filter information from the photometric file

    Parameters
    ----------
    path : str
        path to DES light curve file
    rows : slice
        range of rows for this SN

    Returns
    -------
    dict
        dictionary of filter data for the light curve

    """
    fitstable = table[rows]

    data = {}

    for filt in LSST_FILTERS:
        data[filt] = defaultdict(list)

    for row in fitstable:
        filt = row['FLT'].strip()
        if filt not in LSST_FILTERS:
            continue
        data[filt]['mjd'].append(row['MJD'])
        data[filt]['fluxcal'].append(row['FLUXCAL'])
        data[filt]['fluxcalerr'].append(row['FLUXCALERR'])

    return data


def parse_lsst_header_table(table, index=0):
    """
    Retrieve metadata from header file

    Parameters
    ----------
    path : str
        Pointer to the header FITS file
    index : int, optional
        Row number in the header table (default is 0)
        Corresponds to the SN id in this exposure.

    Returns
    -------
    header : dict
        stripped version of the header
    rows : slice
        range of rows in the corresponding PHOT file
    istarget : bool
        boolean flag to distinguish between train/test sample

    """
    head = table[index]

    header = {}
    # SN ID
    header['snid'] = int(head['SNID'])
    # Redshift
    header['z'] = head['SIM_REDSHIFT_HOST']
    # Type
    header['type'] = head['SIM_NON1a']
    # Peak MJD
    header['pkmjd'] = head['SIM_PEAKMJD']
    # Peak magnitudes
    for filt in LSST_FILTERS:
        header['pkmag_%s' % filt] = head['SIM_PEAKMAG_%s' % filt]
    # Train/Test flag
    istarget = head['SNTYPE'] == -9
    # Corresponding rows in the photometric file
    rows = slice(head['PTROBS_MIN'] - 1, head['PTROBS_MAX'] - 1)

    return header, rows, istarget


def serialize_lsst_sims(path):
    """
    Parse all files in the provided directory and save relevant
    information in a dictionary saved back to disk (and compressed)

    The use of `protocol=2` in the pickling of the files ensures
    data can be unpickled from both Python 2 and 3

    Parameters
    ----------
    path : str
        relative path to a LSST simulated FITS directory

    """
    directory = Path.cwd() / path
    # List all header files in the given directory
    header_files = directory.glob('*HEAD.FITS*')

    train = {}
    target = {}
    for hfile in header_files:
        pfile = hfile.as_posix().replace('HEAD', 'PHOT')
        htable = Table.read(hfile, format='fits')
        ptable = Table.read(pfile, format='fits')
        for idx in range(len(htable)):
            header, rows, istarget = parse_lsst_header_table(htable, idx)
            data = parse_lsst_phot_table(ptable, rows)
            # Add the header info to the light curve data
            data['header'] = header
            # Use the SN id to index the dictionary
            sn_id = header['snid']

            if istarget:
                target[sn_id] = data
            else:
                train[sn_id] = data

    # Use dictionary as base name for the output files
    filename = directory.name
    # Only save non empty dictionaries
    if train:
        with gzip.open(filename + '_train.pkl', 'wb') as output:
            pickle.dump(train, output, protocol=2)
    if target:
        with gzip.open(filename + '_target.pkl', 'wb') as output:
            pickle.dump(target, output, protocol=2)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser("LSST supernovae simulations serializer")
    parser.add_argument('directories', type=str, nargs='+',
                        help="List of simulation directories (MODELS)")
    parser.add_argument('--timed', action='store_true',
                        help="Add a timer")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.timed:
        import time
        start = time.time()

    for directory in args.directories:
        serialize_lsst_sims(directory)
        print("SN data from {} processed".format(directory))

    if args.timed:
        end = time.time()
        secs = end - start
        print("LSST light curves serialized in {:.1f} seconds".format(secs))


if __name__ == '__main__':
    main()
