from src.utils import utils
import wave
import tempfile
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import scipy.stats
import pandas as pd

def analyze_wave_file(input_wav):
    origAudio = wave.open(input_wav,'r')
    frameRate = origAudio.getframerate()
    nChannels = origAudio.getnchannels()
    sampWidth = origAudio.getsampwidth()
    return {"frameRate": frameRate, "nChannels": nChannels, "sampWidth": sampWidth}

def split_wav_file(input_wav):
    output_channel1 = tempfile.NamedTemporaryFile(delete=False, dir=utils.get_project_root() + "/data/tmp/")
    output_channel2 = tempfile.NamedTemporaryFile(delete=False, dir=utils.get_project_root() + "/data/tmp/")

    data = read(input_wav)
    write(output_channel1, data[0], np.array(zip(*data[1])[0]))
    write(output_channel2, data[0], np.array(zip(*data[1])[1]))
    return output_channel1.name, output_channel2.name

def consolidate_intervals(intervals):
    sorted_by_lower_bound = sorted(intervals, key=lambda tup: tup[0])
    merged = []
    for higher in sorted_by_lower_bound:
        if not merged:
            merged.append(higher)
        else:
            lower = merged[-1]
            # test for intersection between lower and higher:
            # we know via sorting that lower[0] <= higher[0]
            if higher[0] <= lower[1]:
                upper_bound = max(lower[1], higher[1])
                merged[-1] = (lower[0], upper_bound)  # replace by merged interval
            else:
                merged.append(higher)
    return merged

def compute_moving_variance(signal_v, sampling_r):
    s = pd.Series(signal_v)
    mvar = list(pd.rolling_std(s, sampling_r).fillna(0))
    # set it back
    mvar = mvar[(sampling_r/2):] + [0]*(sampling_r/2)
    # plt.plot(mvar)
    return mvar

def compute_intervals(signal_v, sig_thresh, sampling_r, padding_sec):
    # loop through variance data and extract intervals based on threshold plus padding
    starts = [i for i in range(len(signal_v)-1) if signal_v[i]<=sig_thresh and signal_v[i+1]>sig_thresh]
    starts = [max(0, s-padding_sec*sampling_r) for s in starts]
    stops = [i for i in range(len(signal_v)-1) if signal_v[i]>=sig_thresh and signal_v[i+1]<sig_thresh ]
    stops = [min(len(signal_v)-1, s+padding_sec*sampling_r) for s in stops]
    return zip(starts,stops)

def compute_signal_threshold(signal_v, bins):
    # bin the moving variance data, and compute the signal threshold
    h = np.histogram(signal_v, bins=bins)
    snr = scipy.stats.signaltonoise(signal_v)
    sig_thresh = h[1][int(bins*(1-snr))]
    return sig_thresh

def intervals_from_signal(signal_v, sampling_r, bins=30, padding_sec=0.5, resample_r=1):
    # resample data for faster compute
    signal_v = list(signal_v)[0::resample_r]
    sampling_r = sampling_r/resample_r
    # compute moving variance
    mvar = compute_moving_variance(signal_v, sampling_r)
    # compute signal threshold over noise
    sig_thresh = compute_signal_threshold(mvar, bins)
    # use threshold to get audio intervals and pad them
    intervals = compute_intervals(mvar, sig_thresh, sampling_r, padding_sec)
    # re-expand signal by resampling factor
    intervals = [(start*resample_r, stop*resample_r) for start,stop in intervals]
    return intervals