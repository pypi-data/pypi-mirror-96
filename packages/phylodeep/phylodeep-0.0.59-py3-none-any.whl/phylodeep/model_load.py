import warnings
import os

import joblib
from tensorflow.python.keras.models import model_from_json

warnings.filterwarnings('ignore')

PRETRAINED_MODELS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pretrained_models')


def model_scale_load_ffnn(tree_size, model):
    pred_method = 'FFNN'
    json_file = open(os.path.join(PRETRAINED_MODELS_DIR, 'models', model + '_' + tree_size + '_' + pred_method +
                                  '.json'), 'r')
    loaded_model = json_file.read()
    json_file.close()

    model_ffnn = model_from_json(loaded_model)
    model_ffnn.load_weights(os.path.join(PRETRAINED_MODELS_DIR, 'weights', model + '_' + tree_size + '_' + pred_method +
                                         '.h5'))
    scaler = joblib.load(os.path.join(PRETRAINED_MODELS_DIR, 'scalers', model + '_' + tree_size + '_' + pred_method +
                                      '.pkl'))

    return model_ffnn, scaler


def model_load_cnn(tree_size, model):
    pred_method = 'CNN'
    json_file = open(os.path.join(PRETRAINED_MODELS_DIR, 'models', model + '_' + tree_size + '_' + pred_method +
                                  '.json'), 'r')
    loaded_model = json_file.read()
    json_file.close()

    model_cnn = model_from_json(loaded_model)
    model_cnn.load_weights(os.path.join(PRETRAINED_MODELS_DIR, 'weights', model + '_' + tree_size + '_' + pred_method +
                                        '.h5'))

    return model_cnn
