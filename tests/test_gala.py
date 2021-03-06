
from numpy.testing import assert_array_equal, assert_allclose
from numpy.testing.decorators import skipif
import numpy as np
import os
from gala import imio, classify, features, agglo, evaluate as ev

# load example data

gt_train, pr_train, p4_train, ws_train = map(imio.read_h5_stack, ['example-data/train-gt.lzf.h5', 'example-data/train-p1.lzf.h5', 'example-data/train-p4.lzf.h5', 'example-data/train-ws.lzf.h5'])
gt_test, pr_test, p4_test, ws_test = map(imio.read_h5_stack, ['example-data/test-gt.lzf.h5', 'example-data/test-p1.lzf.h5', 'example-data/test-p4.lzf.h5', 'example-data/test-ws.lzf.h5'])

# prepare feature manager
fm = features.moments.Manager()
fh = features.histogram.Manager()
fc = features.base.Composite(children=[fm, fh])


def load_training_data(fn):
    io = np.load(fn)
    return io['X'], io['y']


# this training set should be created by the below command, but setting
# np.random.RandomState() and before saving it does not remove all
# differences from the training data set at create and test time.
@skipif(not os.path.isfile('example-data/train-set.npz'))
def test_training_1channel():
    g_train = agglo.Rag(ws_train, pr_train, feature_manager=fc)
    np.random.RandomState(0)
    (X, y, w, merges) = g_train.learn_agglomerate(gt_train, fc)[0]
    X_expected, y_expected = load_training_data('example-data/train-set.npz')
    assert_allclose(X, X_expected, atol=1e-6)
    assert_allclose(y, y_expected, atol=1e-6)


def test_learned_agglo_1channel():
    rf = classify.load_classifier('example-data/rf1.joblib')
    learned_policy = agglo.classifier_probability(fc, rf)
    g_test = agglo.Rag(ws_test, pr_test, learned_policy, feature_manager=fc)
    g_test.agglomerate(0.5)
    seg_test1 = g_test.get_segmentation()
    seg_test1_result = imio.read_h5_stack('example-data/test-seg1.lzf.h5')
    assert_array_equal(seg_test1, seg_test1_result)


# this training set should be created by the below command, but setting
# np.random.RandomState() and before saving it does not remove all
# differences from the training data set at create and test time.
@skipif(not os.path.isfile('example-data/train-set4.npz'))
def test_training_4channel():
    g_train4 = agglo.Rag(ws_train, p4_train, feature_manager=fc)
    np.random.RandomState(0)
    (X4, y4, w4, merges4) = g_train4.learn_agglomerate(gt_train, fc)[0]
    X4_expected, y4_expected = load_training_data('example-data/train-set4.npz')
    assert_allclose(X4, X4_expected, atol=1e-6)
    assert_allclose(y4, y4_expected, atol=1e-6)


def test_learned_agglo_4channel():
    rf4 = classify.load_classifier('example-data/rf4.joblib')
    learned_policy4 = agglo.classifier_probability(fc, rf4)
    g_test4 = agglo.Rag(ws_test, p4_test, learned_policy4, feature_manager=fc)
    g_test4.agglomerate(0.5)
    seg_test4 = g_test4.get_segmentation()
    seg_test4_result = imio.read_h5_stack('example-data/test-seg4.lzf.h5')
    assert_array_equal(seg_test4, seg_test4_result)


def test_split_vi():
    seg_test1 = imio.read_h5_stack('example-data/test-seg1.lzf.h5')
    seg_test4 = imio.read_h5_stack('example-data/test-seg4.lzf.h5')
    result = np.vstack((
        ev.split_vi(ws_test, gt_test),
        ev.split_vi(seg_test1, gt_test),
        ev.split_vi(seg_test4, gt_test)
        ))
    expected = np.load('example-data/vi-results.npy')
    assert_allclose(result, expected, atol=1e-6)


if __name__ == '__main__':
    np.random.RandomState(0)
    from numpy import testing
    testing.run_module_suite()

