#!/usr/bin/env python3
"""Check (or write, with --write) the stim_id column of every task-action events.tsv of on007353 (HAD-MEEG).

usage: python code/check_stim_id.py [--write]        (run from the root of this dataset)

stim_id is derived from files of this dataset only; no other dataset is read.

For each EEG and MEG run of each participant:
  1. The run's 'video on' rows, in file order, are paired with the 'video_on' trials of the same session and run in
     derivatives/detailed_events/sub-XX_events.tsv (written by the dataset authors), in file order. The two counts
     must be equal.
  2. detailed_events gives the class and YouTube id of each trial. stimuli/stimuli.tsv has one row per clip file;
     its stim_id is v_<class>_id_<YouTube id>_start_<s>_label_1. If exactly one clip has that class and YouTube id,
     the row's stim_id is that clip. If several clips share them (the same YouTube video cut at two or three start
     times), detailed_events does not say which one was shown, and stim_id is n/a.
  3. Every row that is not 'video on' has stim_id n/a.
Without --write it compares the expected column with the files and exits 1 on any difference; with --write it
rewrites only the stim_id column (last column) and leaves every other byte of the file unchanged.
"""
import collections
import csv
import glob
import re
import sys

PAT = re.compile(r"v_(.+)_id_(.+)_start_[0-9.]+_label_\d+$")


def read_tsv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def norm(s):
    return s.replace(" ", "_")


def main(write):
    by_pair = collections.defaultdict(list)
    for r in read_tsv("stimuli/stimuli.tsv"):
        m = PAT.match(r["stim_id"])
        by_pair[(norm(m.group(1)), m.group(2))].append(r["stim_id"])

    det = collections.defaultdict(list)
    for p in sorted(glob.glob("derivatives/detailed_events/sub-*_events.tsv")):
        for r in read_tsv(p):
            if r["event_name"] == "video_on":
                det[(int(r["subject"]), r["session"], int(r["run"]))].append(r)

    c = collections.Counter()
    problems = []
    for ev in sorted(glob.glob("sub-*/ses-*/*/sub-*_ses-*_task-action_run-*_events.tsv")):
        m = re.match(r"sub-(\d+)/ses-(eeg|meg)/.*_run-(\d+)_events\.tsv$", ev)
        key = (int(m.group(1)), m.group(2), int(m.group(3)))
        c["events_files"] += 1
        with open(ev, newline="", encoding="utf-8") as f:
            raw = f.read()
        lines = raw.split("\n")
        end = "\n" if raw.endswith("\n") else ""
        if end:
            lines = lines[:-1]
        hdr = lines[0].split("\t")
        if hdr[-1] != "stim_id":
            problems.append(f"{ev}: stim_id is not the last column")
            continue
        it = iter(det.get(key, []))
        n_det = len(det.get(key, []))
        n_on = 0
        out = [lines[0]]
        for line in lines[1:]:
            cells = line.split("\t")
            tt = cells[hdr.index("trial_type")]
            want = "n/a"
            if tt == "video on":
                n_on += 1
                d = next(it, None)
                if d is None:
                    problems.append(f"{ev}: more 'video on' rows than detailed_events trials")
                else:
                    cands = by_pair.get((norm(d["class_name"]), d["video_id"]), [])
                    if len(cands) == 1:
                        want = cands[0]
                        c["video_on_identified"] += 1
                    elif len(cands) > 1:
                        c["video_on_unresolved_several_clips"] += 1
                    else:
                        c["video_on_no_clip_in_stimuli"] += 1
                c["video_on_rows"] += 1
            if cells[-1] != want:
                c["cells_differing"] += 1
            cells[-1] = want
            out.append("\t".join(cells))
        if n_on != n_det:
            problems.append(f"{ev}: {n_on} 'video on' rows, {n_det} detailed_events trials")
        if write:
            new = "\n".join(out) + end
            if new != raw:
                with open(ev, "w", newline="", encoding="utf-8") as f:
                    f.write(new)
                c["files_written"] += 1

    for k in ["events_files", "video_on_rows", "video_on_identified", "video_on_unresolved_several_clips",
              "video_on_no_clip_in_stimuli", "cells_differing", "files_written"]:
        print(f"{k}: {c[k]}")
    print(f"problems: {len(problems)}")
    for p in problems[:50]:
        print("  ", p)
    if problems:
        return 1
    return 0 if (write or c["cells_differing"] == 0) else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    if args not in ([], ["--write"]):
        sys.exit(__doc__)
    sys.exit(main(args == ["--write"]))
