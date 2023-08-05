# -*- coding: utf8
"""This file contains some utils function to deal with data and load and save models."""
import os
from os.path import join, exists
import pickle
import json
from pathlib import Path

import numpy as np
from sklearn.utils import check_random_state
import requests


def get_ml_data_dir_path():
    """Get the data directory folder from the JSON config file.

    Return
    -------
    pathlib.Path, location of the data folder.
    """
    sys_lighton_cfg = Path('/etc/lighton.json')
    user_lighton_cfg = Path.home()/'.lighton.json'

    if sys_lighton_cfg.is_file():
        config_data = json.loads(sys_lighton_cfg.read_text())
    elif user_lighton_cfg.is_file():
        config_data = json.loads(user_lighton_cfg.read_text())
    else:
        raise FileNotFoundError("Can't find a lighton.json folder.")
    return Path(config_data['ml_data_path'])


def download(url, directory):
    """Download data from `url` into `directory`"""
    filename = join(directory, url.split("/")[-1])
    r = requests.get(url)
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(r.content)
    else:
        raise IOError('Unsuccessful request, code {}'.format(r.status_code))


def load_model(model_path):
    """Loads the model from a pickle file.

    Parameters
    ----------
    model_path : str,
        path for the pickle file of the model.

    Returns
    -------
    model : BaseEstimator, RegressorMixin or TransformerMixin and children,
        instance of the model.

    """
    if not exists(model_path):
        raise FileNotFoundError(model_path + " doesn't exist")

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    return model


def save_model(model, model_name, model_path):
    """Saves a model in a pickle file.

    Parameters
    ----------
    model : BaseEstimator, RegressorMixin or TransformerMixin and children,
        instance of the model to save.
    model_name : str,
        name of the pickle file of the saved model.
    model_path : str,
        path for the directory of the pickle file of the saved model.

    """
    print('Saving model...')
    # Check if the folder exists
    if not exists(model_path):
        os.mkdir(model_path)
    with open(join(model_path, model_name), 'wb') as f:
        pickle.dump(model, f)


def select_subset(X, y, classes=range(10), ratio=1, random_state=None):
    """Selects a subset of a dataset.

    Parameters
    ----------
    X : 2D np.ndarray,
        input data.
    y : np.ndarray,
        targets.
    classes : list or np.ndarray,
        number of classes in the dataset.
    ratio : float,
        controls the ratio between examples.
    random_state : int, RandomState instance or None, optional, defaults to None,
        controls the pseudo random number generator used to subsample the dataset.

    Returns
    -------
    X : np.ndarray,
        subsampled data.
    y : np.ndarray,
        subsampled targets.

    """
    ind_sel = np.in1d(y, np.asarray(classes))
    ind_sel = np.where(ind_sel)[0]
    n_samples = len(ind_sel)

    if ratio != 1:
        random_state = check_random_state(random_state)
        ind_sel = random_state.choice(ind_sel, size=int(n_samples * ratio), replace=False)

    X, y = X[ind_sel], y[ind_sel]

    return X, y


def load_data_from_numpy_archive(path_to_file):
    """Loads data from NumPy archive.

    Parameters
    ----------
    path_to_file : str,
        path to the numpy archive to load.

    Returns
    -------
    (X_train, y_train) : tuple of np.ndarray,
        train set.
    (X_test, y_test) : tuple of np.ndarray,
        test set.

    """
    if not os.path.exists(path_to_file):
        raise FileNotFoundError(path_to_file + " does not exist")

    data = np.load(path_to_file)
    X_train, y_train = data['X_train'], data['y_train']
    X_test, y_test = data['X_test'], data['y_test']

    return (X_train, y_train), (X_test, y_test)


def cast_01_to_uint8(X):
    """Casts binary data to uint8.

    Parameters
    ----------
    X : np.ndarray,
        input data.

    Returns
    -------
    X_uint8 : np.ndarray,
        input data in uint8.

    """
    X_uint8 = np.round(255 * X).astype(np.uint8)
    return X_uint8
