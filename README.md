[![DOI](https://img.shields.io/badge/DOI-10.82901%2Fnemar.on007353-blue)](https://doi.org/10.82901/nemar.on007353)

Human action recognition is a core component of social cognition, engaging spatially distributed and temporally evolving neural responses that encode visual information and infer intention. To map the brain’s spatial organization supporting this process, we previously released the Human Action Dataset (HAD), a functional magnetic resonance imaging (fMRI) resource. However, fMRI’s limited temporal resolution constrains its ability to capture rapid neural dynamics. Here, we present the HAD-MEEG dataset, which extends HAD-fMRI, leveraging the millisecond-level temporal resolution of magnetoencephalography (MEG) and electroencephalography (EEG). HAD-MEEG were recorded in the same participants and with the same stimuli as HAD-fMRI, in which 30 participants viewed 21,600 video clips spanning 180 categories of human action. By integrating the temporal precision of M/EEG with the spatial precision of fMRI, HAD enables comprehensive spatiotemporal investigation of the neural mechanisms underlying human action recognition.

## Stimuli

`stimuli/` holds the 21,600 clips (180 action classes x 120) as deposited by the authors: HACS clips cut from YouTube videos
(third-party content). File names give the YouTube id and the start second, `v_<class>_id_<YouTube id>_start_<s>_label_1.mp4`.

Added 2026-10-08 (metadata only, no media added):
- `stimuli/stimuli.tsv` + `stimuli.json`: one row per clip with its path, YouTube id, start, duration, frame rate, size,
  frame count, audio track and SHA-256 (all clips 256 x 256 pixels, 2.0-2.1 s; 14 clips have no audio stream).
- A `stim_id` column in every `sub-*_ses-{eeg,meg}_task-action_run-*_events.tsv`: the clip shown at each `video on` event
  (its file name without `.mp4`; n/a on other rows), described in each run's `_events.json`; the path is in
  `stimuli/stimuli.tsv`. (BIDS `stim_file` is not used because bids-validator rejects the spaces in this dataset's class
  folder names inside `stim_file` paths.)

How the event-to-clip mapping was obtained: the released events carry no clip identity. `derivatives/detailed_events`
(written by the dataset authors) gives the class and YouTube id of every trial, in the order of the events files, but not the
start second. Each `video on` row is paired with the `video_on` trial of the same session and run, in order. Where exactly one
clip in `stimuli/` has that class and YouTube id, `stim_id` names it: 40,388 of the 41,760 `video on` rows (EEG and MEG).
In the other 1,372 rows the same YouTube video was cut at two or three start times, the event table does not say which cut
was shown, and `stim_id` is n/a. Only files of this dataset are used; no other dataset is linked.

To check the mapping yourself: `python code/check_stim_id.py` from the root of this dataset (plain git files only). It
recomputes every `stim_id` from `derivatives/detailed_events` and `stimuli/stimuli.tsv` and reports any difference. On this
version: 464 events files, 41,760 `video on` rows, 40,388 identified, 1,372 n/a, 0 differences.
