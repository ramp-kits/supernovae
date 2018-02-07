from __future__ import print_function

import os
import gzip
import pickle
import pandas as pd
import numpy as np

import rampwf as rw
from sklearn.model_selection import StratifiedShuffleSplit

problem_title = 'PLAsTiCC transient classification RAMP'
_prediction_label_names = [0, 1]

# A type (class) which will be used to create wrapper objects for y_pred
Predictions = rw.prediction_types.make_multiclass(
    label_names=_prediction_label_names)

# An object implementing the workflow
workflow = rw.workflows.FeatureExtractorClassifier()


score_types = [
    rw.score_types.ROCAUC(name='auc'),
    rw.score_types.Accuracy(name='acc'),
    rw.score_types.NegativeLogLikelihood(name='nll'),
]


def get_cv(X, y):
    cv = StratifiedShuffleSplit(n_splits=3, test_size=0.2, random_state=42)
    return cv.split(X, y)


def _read_data(path, f_name):
    test = os.getenv('RAMP_TEST_MODE', 0)

    if test:
        suffix = '_mini'
    else:
        suffix = ''

    data_path = os.path.join(path, 'data', 'des_{type}{suffix}.pkl'.format(
        type=f_name, suffix=suffix))

    try:
        with gzip.open(data_path, 'rb') as f:
            data = pickle.load(f)
    except IOError:
        raise IOError("'{} not found. Ensure you ran "
                      "'python download_data.py' to "
                      "obtain the train/test data".format(data_path))

    X_df = to_df(data)
    sntype = X_df.type
    X_df = X_df.drop(columns=['type'])
    y = pd.get_dummies(sntype == 0, prefix='SNIa', drop_first=True)
    y_array = y.values.ravel()

    return X_df, y_array


def to_df(data):
    for idx in data:
        sn = data[idx]
        for filt in 'griz':
            sn['%s_mjd' % filt] = np.array(sn[filt]['mjd'])
            sn['%s_fluxcal' % filt] = np.array(sn[filt]['fluxcal'])
            sn['%s_fluxcalerr' % filt] = np.array(sn[filt]['fluxcalerr'])
            del sn[filt]
        sn.update(sn['header'])
        del sn['header']

    return pd.DataFrame.from_dict(data, orient='index')


def get_train_data(path='.'):
    return _read_data(path, 'train')


def get_test_data(path='.'):
    return _read_data(path, 'test')
