#!/usr/bin/env python

import mne
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from glob import glob
from matplotlib import interactive
from pathlib import Path

# plotting settings
import matplotlib
interactive(True)
mne.set_log_level("info")
#matplotlib.use('QT5Agg')

# Set a few global variables
# The data is not preconditioned unless this variable is reset
preconditioned = False

from .config import (
    channel_types,
    reject_criteria,
    flat_criteria,
    crosstalk_file,
    fine_cal_file,
    subject_list,
    event_dict,
)

# Define data processing functions and helper functions



def _get_channel_subsets(raw):
    """
    Return defined sensor locations as a list of relevant sensors
    """
    # TODO: fill in with sensor names for left and right
    parietal_left = mne.read_selection(name=["Left-parietal"], info=raw.info)
    parietal_right = mne.read_selection(name=["Right-parietal"], info=raw.info)
    occipital_left = mne.read_selection(name=["Left-occipital"], info=raw.info)
    occipital_right = mne.read_selection(name=["Right-occipital"], info=raw.info)
    frontal_left = mne.read_selection(name=["Left-frontal"], info=raw.info)
    frontal_right = mne.read_selection(name=["Right-frontal"], info=raw.info)
    vertex_sensors = mne.read_selection(name=["Vertex"], info=raw.info)
    temporal_left = mne.read_selection(name=["Left-temporal"], info=raw.info)
    temporal_right = mne.read_selection(name=["Right-temporal"], info=raw.info)
    sensors = {
        "lpar": parietal_left,
        "rpar": parietal_right,
        "locc": occipital_left,
        "rocc": occipital_right,
        "lfro": frontal_left,
        "rfro": frontal_right,
        "ltem": temporal_left,
        "rtem": temporal_right,
        "ver": vertex_sensors,
    }
    return sensors


def _check_if_bids_directory_exists(outpath):
    """
    Helper function that checks if a directory exists, and if not, creates it.
    """
    check_dir = os.path.dirname(outpath)
    print(check_dir)
    if not os.path.isdir(Path(check_dir)):
        print(
            f"The BIDS directory {check_dir} does not seem to exist. "
            f"Attempting creation..."
        )
        os.makedirs(Path(check_dir))


def _construct_path(components):
    """
    Helper function to construct a path to save a file or figure in, check if
    the directory exists, and create the path recursively, if necessary.

    :params components: list, path components
    """
    fpath = os.path.join(*components)
    _check_if_bids_directory_exists(fpath)
    return fpath


def eventreader(raw, subject, event_dict, outputdir="/tmp/"):
    """
    the Triggers 32790 32792 seem spurious. TODO.
    :param raw:
    :return:
    """
    # for some reason, events only start at sample 628416 (sub 4)
    events = mne.find_events(
        raw,
        min_duration=0.002,  # ignores spurious events
        uint_cast=True,  # workaround an Elekta acquisition bug that causes negative values
        # initial_event=True # unsure - the first on is 32772
    )

    # plot events. This works without raw data
    fig = mne.viz.plot_events(
        events,
        sfreq=raw.info["sfreq"],
        first_samp=raw.first_samp,
        event_id=event_dict,
        on_missing="warn",
    )
    fig.suptitle(
        "Full event protocol for {} ({})".format(
            raw.info["subject_info"]["first_name"],
            raw.info["subject_info"]["last_name"],
        )
    )
    fpath = _construct_path(
        [
            Path(outputdir),
            f"sub-{subject}",
            "meg",
            f"sub-{subject}_task-memento_eventplot.png",
        ]
    )
    fig.savefig(str(fpath))
    return events


def epoch_data(
    raw,
    events,
    event_dict,
    subject,
    conditionname=None,
    sensor_picks=None,
    picks=None,
    pick_description=None,
    figdir='/tmp',
    reject_criteria=None,
    tmin=-0.2,
    tmax=0.7,
    reject_bad_epochs=True,
    autoreject=False,
):
    """
    Create epochs from specified events.
    :param tmin: int, start time before event. Defaults to -0.2 in MNE 0.23dev
    :param tmax: int, end time after event. Defaults to 0.5 in MNE 0.23dev
    :param sensor_picks: list, sensors that should be plotted separately
    :param picks: list, sensors that epoching should be restricted to
    :param pick_description: str, a short description (no spaces) of the picks,
    e.g., 'occipital' or 'motor'.
    :param figdir: str, Path to where diagnostic plots should be saved.

    TODO: we could include a baseline correction
    TODO: figure out projections -> don't use if you can use SSS
    TODO: autoreject requires picking only MEG channels in epoching
    """

    epoch_params = {
        "raw": raw,
        "events": events,
        "event_id": event_dict,
        "tmin": tmin,
        "tmax": tmax,
        "preload": True,
        "on_missing": "warn",
        "verbose": True,
        "picks": picks,
    }

    if reject_bad_epochs and not autoreject:
        # we can reject based on predefined criteria. Add it as an argument to
        # the parameter list
        epoch_params["reject"] = reject_criteria
    else:
        epoch_params["reject"] = None

    epochs = mne.Epochs(**epoch_params)
    if reject_bad_epochs and not autoreject:
        epochs.plot_drop_log()
    if autoreject:
        # if we want to perform autorejection of epochs using the autoreject tool
        for condition in conditionname:
            # do this for all relevant conditions
            epochs = autoreject_bad_epochs(
                epochs=epochs, picks=picks, key=condition
            )

    for condition in conditionname:
        _plot_epochs(
            raw,
            epochs=epochs,
            subject=subject,
            key=condition,
            figdir=figdir,
            picks=sensor_picks,
            pick_description=pick_description,
        )
    return epochs


def _plot_epochs(
    raw,
    epochs,
    subject,
    key,
    figdir,
    picks,
    pick_description,
):
    """

    TODO: decide for the right kinds of plots, and whether to plot left and right
    seperately,
    :param picks: list, all channels that should be plotted. You can also select
    predefined locations: lpar, rpar, locc, rocc, lfro, rfro, ltem, rtem, ver.
    :param pick_description: str, a short description (no spaces) of the picks,
    e.g., 'occipital' or 'motor'.
    """
    # subselect the required condition. For example visuals = epochs['visualfirst']
    wanted_epochs = epochs[key]
    average = wanted_epochs.average()
    # Some general plots over all channels
    _plot_evoked_fields(data=average,
                        subject=subject,
                        figdir=figdir,
                        key=key,
                        location='avg-epoch-all')
    if picks:
        # If we want to plot a predefined sensor space, e.g., right parietal or left
        # temporal, load in those lists of sensors
        assert type(picks) == list
        if len(picks) >= 2:
            # more than one selection in this list
            sensors = _get_channel_subsets(raw)
            mypicklist = []
            for p in picks:
                if p in sensors.keys():
                    mypicklist.extend(sensors[p])
                else:
                    mypicklist.extend(p)
            subset = epochs.pick_channels(mypicklist)
            subset_average = subset.average()
            _plot_evoked_fields(data=subset_average,
                                subject=subject,
                                figdir=figdir,
                                key=key,
                                location=pick_description)

            #TODO plot with pick_description

    return


def _plot_evoked_fields(data, subject, figdir, key='unnamed', location='avg-epoch-all'):
    """
    Helper to plot evoked field with all available plots
    :return:
    """
    # make joint plot of topographies and sensors
    figpath_grad = _construct_path(
        [
            Path(figdir),
            f"sub-{subject}",
            "meg",
            f"sub-{subject}_task-memento_{location}_cond-{key}_joint-grad.png",
        ]
    )
    figpath_mag = _construct_path(
        [
            Path(figdir),
            f"sub-{subject}",
            "meg",
            f"sub-{subject}_task-memento_{location}_cond-{key}_joint-mag.png",
        ]
    )
    fig = data.plot_joint()
    fig1 = fig[0]
    fig2 = fig[1]
    fig1.savefig(figpath_grad)
    fig2.savefig(figpath_mag)
    # also plot topographies
    figpath = _construct_path(
        [
            Path(figdir),
            f"sub-{subject}",
            "meg",
            f"sub-{subject}_task-memento_{location}_cond-{key}_topography.png",
        ]
    )
    fig = data.plot_topo()
    fig.savefig(figpath)
    # also save the data as an image
    figpath = _construct_path(
        [
            Path(figdir),
            f"sub-{subject}",
            "meg",
            f"sub-{subject}_task-memento_{location}_cond-{key}_image.png",
        ]
    )
    fig = data.plot_image()
    fig.savefig(figpath)


def evoked_visual_potentials(raw,
                             subject,
                             event_dict,
                             figdir="/tmp/"):
    """
    Function to plot visual potentials from the first visual option (left) as a
    sanity check
    """

    events = eventreader(raw=raw, subject=subject, outputdir=figdir,
                         event_dict=event_dict)

    visual_epochs = epoch_data(raw=raw,
                               events=events,
                               event_dict=event_dict,
                               subject=subject,
                               conditionname=['visualfirst'],
                               sensor_picks=['locc', 'rocc'],
                               picks=None,
                               pick_description='occipital',
                               figdir=figdir,
                               tmax=0.7,
                               tmin=-0.2,
                               reject_criteria=reject_criteria,
                               reject_bad_epochs=True,
                               autoreject=False)


def _getNeuromagRegions(meg,
                       label,
                       ch_type="both"):
    """
    returns the indices of channels in a certain region of the Neuromag sensor space
    meg: Raw, Epoch, Evoked (or anything that has the “ch_names” field)
    label: list, str which region to extract. Possible fields are: Left-frontal, Right-frontal, Left-temporal, Right-temporal, Left-parietal, Right-parietal, Left-occipital, Right-occipital
    type: grads, mags or both
    returns a sorted list of indices that match the provided label
    """
    import re

    if isinstance(label,str):
        label = [label]
    if ch_type == 'mags':
        p = re.compile('MEG\d\d\d1')
    elif ch_type == 'grads':
        p = re.compile('MEG\d\d\d[2-3]')
    else:
        p = re.compile('MEG\d\d\d[1-3]')

    # extract channel labels from meg object
    sel = set()
    for l in label:
        sel = sel.union({ch.replace('MEG ', 'MEG') for ch in mne.selection.read_selection(l)})
    sel = list(sel)

    # use regexp to find only grads or mags
    channels = re.findall(p,'|'.join(sel))

    # get indices
    l = []
    for ch in channels:
        l.append(meg.ch_names.index(ch))

    return sorted(l)


def autoreject_bad_epochs(epochs, key):
    import autoreject
    import numpy as np

    # these values come straight from the tutorial:
    # http://autoreject.github.io/auto_examples/plot_auto_repair.html
    n_interpolates = np.array([1, 4, 32])
    consensus_percs = np.linspace(0, 1.0, 11)
    #important: Requires epochs with only MEG sensors, selected during epoching!
    ar = autoreject.AutoReject(
        n_interpolates,
        consensus_percs,
        thresh_method="random_search",
        random_state=42,
    )
    subset = epochs[key]
    ar.fit(subset)
    epochs_clean = ar.transform(subset)
    return epochs_clean


def artifacts(raw):
    # see https://mne.tools/stable/auto_tutorials/preprocessing/plot_10_preprocessing_overview.html#sphx-glr-auto-tutorials-preprocessing-plot-10-preprocessing-overview-py
    # low frequency drifts in magnetometers
    mag_channels = mne.pick_types(raw.info, meg="mag")
    raw.plot(
        block=True,
        duration=60,
        order=mag_channels,
        n_channels=len(mag_channels),
        remove_dc=False,
    )

    # power line noise
    fig = raw.plot_psd(block=True, tmax=np.inf, fmax=250, average=True)

    # heartbeat artifacts
    ecg_epochs = mne.preprocessing.create_ecg_epochs(raw)
    avg_ecg_epochs = ecg_epochs.average().apply_baseline((-0.5, -0.2))
