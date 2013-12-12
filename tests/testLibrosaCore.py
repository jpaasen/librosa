#!/usr/bin/env python
# CREATED:2013-03-08 15:25:18 by Brian McFee <brm2132@columbia.edu>
#  unit tests for librosa core (__init__.py)
#
# Run me as follows:
#   cd tests/
#   nosetests -v
#
# This test suite verifies that librosa core routines match (numerically) the output
# of various DPWE matlab implementations on a broad range of input parameters.
#
# All test data is generated by the Matlab script "makeTestData.m".
# Each test loads in a .mat file which contains the input and desired output for a given
# function.  The test then runs the librosa implementation and verifies the results
# against the desired output, typically via numpy.allclose().
#
# CAVEATS:
#   Currently, not all tests are exhaustive in parameter space.  This is typically due
#   restricted functionality of the librosa implementations.  Similarly, there is no
#   fuzz-testing here, so behavior on invalid inputs is not yet well-defined.
#

import librosa
import glob
import numpy, scipy.io

from nose.tools import nottest

#-- utilities --#
def files(pattern):
    test_files = glob.glob(pattern)
    test_files.sort()
    return test_files

def load(infile):
    DATA = scipy.io.loadmat(infile, chars_as_strings=True)
    return DATA
#--           --#

#-- Tests     --#
def test_load():
    # Note: this does not test resampling.
    # That is a separate unit test.

    def __test(infile):
        DATA    = load(infile)
        (y, sr) = librosa.load(DATA['wavfile'][0], sr=None, mono=DATA['mono'])

        # Verify that the sample rate is correct
        assert sr == DATA['sr']

        assert numpy.allclose(y, DATA['y'])

    for infile in files('data/core-load-*.mat'):
        yield (__test, infile)
    pass

@nottest
def test_resample():

    def __test(infile):
        DATA    = load(infile)
        
        # load the wav file
        (y_in, sr_in) = librosa.load(DATA['wavfile'][0], sr=None, mono=True)

        # Resample it to the target rate
        y_out = librosa.resample(y_in, DATA['sr_in'], DATA['sr_out'])

        # Are we the same length?
        if len(y_out) == len(DATA['y_out']):
            # Is the data close?
            assert numpy.allclose(y_out, DATA['y_out'])
        elif len(y_out) == len(DATA['y_out']) - 1:
            assert (numpy.allclose(y_out, DATA['y_out'][:-1,0]) or
                    numpy.allclose(y_out, DATA['y_out'][1:,0]))
        elif len(y_out) == len(DATA['y_out']) + 1:
            assert (numpy.allclose(y_out[1:], DATA['y_out']) or
                    numpy.allclose(y_out[:-2], DATA['y_out']))
        else:
            assert False
        pass

    for infile in files('data/core-resample-*.mat'):
        yield (__test, infile)
    pass

def test_stft():

    def __test(infile):
        DATA    = load(infile)

        # Load the file
        (y, sr) = librosa.load(DATA['wavfile'][0], sr=None, mono=True)

        # Compute the STFT
        D       = librosa.stft(y,       n_fft       =   DATA['nfft'][0,0].astype(int),
                                        win_length  =   DATA['hann_w'][0,0].astype(int),
                                        hop_length  =   DATA['hop_length'][0,0].astype(int))

        assert  numpy.allclose(D, DATA['D'])   


    for infile in files('data/core-stft-*.mat'):
        yield (__test, infile)
    pass

def test_ifgram():

    def __test(infile):
        DATA    = load(infile)

        y, sr   = librosa.load(DATA['wavfile'][0], sr=None, mono=True)

        # Compute the IFgram
        F, D    = librosa.ifgram(y, n_fft       =   DATA['nfft'][0,0].astype(int),
                                    hop_length  =   DATA['hop_length'][0,0].astype(int),
                                    win_length  =   DATA['hann_w'][0,0].astype(int),
                                    sr          =   DATA['sr'][0,0].astype(int))

        # D fails to match here because of fftshift()
        # assert numpy.allclose(D, DATA['D'])
        assert numpy.allclose(F, DATA['F'])

    for infile in files('data/core-ifgram-*.mat'):
        yield (__test, infile)

    pass
def test_magphase():

    (y, sr) = librosa.load('data/test1_22050.wav')

    D = librosa.stft(y)

    S, P = librosa.magphase(D)

    assert numpy.allclose(S * P, D)

def test_istft():
    def __test(infile):
        DATA    = load(infile)

        Dinv    = librosa.istft(DATA['D'],  win_length  = DATA['hann_w'][0,0].astype(int),
                                            hop_length  = DATA['hop_length'][0,0].astype(int))
        assert numpy.allclose(Dinv, DATA['Dinv'])

    for infile in files('data/core-istft-*.mat'):
        yield (__test, infile)
    pass

