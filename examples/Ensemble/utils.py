import logging
from sklearn.model_selection import train_test_split

from . import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_train_test_data(df):
    X = df[config.DATA_FEATURES].values
    y = df[config.DATA_TARGETS].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, shuffle=True, random_state=10)
    logger.info('%s, %s, %s, %s', X_train.shape, X_test.shape, y_train.shape, y_test.shape)
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test
    }
