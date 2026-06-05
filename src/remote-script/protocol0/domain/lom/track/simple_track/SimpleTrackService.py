from typing import Optional, List

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


def rename_tracks(tracks: List[SimpleTrack], track_name: Optional[str] = None) -> None:
    """Rename track with duplicate names by numbering them"""
    return None

    # tracks_by_base_name = defaultdict(list)
    #
    # for t in tracks:
    #     if track_name and track_base_name(t.name) != track_base_name(track_name):
    #         continue
    #
    #     tracks_by_base_name[track_base_name(t.name)].append(t)
    #
    # for same_name_tracks in tracks_by_base_name.values():
    #     if len(same_name_tracks) > 1:
    #         for index, track in enumerate(same_name_tracks):
    #             name = track_base_name(track.name, to_lower=False)
    #             if index > 0:
    #                 name = f"{name} {index + 1}"
    #             track.name = name
    #     elif len(same_name_tracks) == 1:
    #         same_name_tracks[0].name = title(
    #             track_base_name(same_name_tracks[0].name, to_lower=False)
    #         )
