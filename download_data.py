from __future__ import print_function

import os

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

URLBASE = 'https://storage.ramp.studio/supernovae/{}'
DATA = [
    'des_train.pkl',
    'des_test.pkl']
TEST_DATA = [
    'des_train_mini.pkl',
    'des_test_mini.pkl']


def main(filenames, output_dir='data'):
    urls = [URLBASE.format(filename) for filename in filenames]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for url, filename in zip(urls, filenames):
        output_file = os.path.join(output_dir, filename)

        if os.path.exists(output_file):
            continue

        print("Downloading from {} ...".format(url))
        urlretrieve(url, filename=output_file)
        print("=> File saved as {}".format(output_file))


if __name__ == '__main__':
    main(DATA + TEST_DATA)
