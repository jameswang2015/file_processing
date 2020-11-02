import argparse
import sys
import json
from pydantic import BaseModel, conlist
from typing import Any, Dict


class AddNewPlaylist(BaseModel):
    """
    define AddNewPlaylist model for data validation
    :user_id: str
    :songs: constraint list, minimum length is 1
    """
    user_id: str
    songs: conlist(str, min_items=1)


class RemovePlaylist(BaseModel):
    """
    define RemovePlaylist model for data validation
    :playlist_id: str
    """
    playlist_id: str


class AddSongToPlaylist(BaseModel):
    """
    define AddSoneToPlaylist model for data validation
    :song_id: str
    :playlist_id: str
    """
    song_id: str
    playlist_id: str


def _get_playlist_id(mixtape: Dict[Any, Any]) -> str:
    """
    the new playlist_id is generated as max_existing_playlist_id + 1
    :param mixtape: input data
    :return: playlist_id as string
    """
    if not mixtape["playlists"]:
        return "1"
    return str(max([int(pl["id"]) for pl in mixtape["playlists"]]) + 1)


def _add_new_playlist(new_playlist: AddNewPlaylist, mixtape: Dict[Any, Any]) -> None:
    """
    add new playlist into playlists
    :param new_playlist: provide user_id and song_ids
    :param mixtape: the data where the new playlist will be added into
    :return: None

    Note: playplist_id will be the current max playlist_id + 1
    """
    # if user_id does not exist in users of mixtape
    # report it, do NOT add it and move to next
    user_ids = {user["id"] for user in mixtape["users"]}
    if new_playlist.user_id not in user_ids:
        print(f"{new_playlist.user_id} does not exist in users")
        return

    playlist_id = _get_playlist_id(mixtape)
    mixtape["playlists"].append({"id": playlist_id,
                                 "user_id": new_playlist.user_id,
                                 "song_ids": new_playlist.songs})
    print(f"successfully added new playlist_id {playlist_id}")


def _remove_playlist(remove_playlist: RemovePlaylist, mixtape: Dict[Any, Any]) -> None:
    """
    Remove playlist from mixtape
    :param remove_playlist: provide playlist_id to be removed
    :param mixtape: the data where playlist will be removed from
    :return: None
    """
    # if playlist_id does not exist, report it and move on
    playlist_index_to_remove = [index for index, pl in enumerate(mixtape["playlists"])
                                if pl["id"] == remove_playlist.playlist_id]
    if not playlist_index_to_remove:
        print(f"{remove_playlist.playlist_id} does not exist!")
        return

    mixtape["playlists"].pop(playlist_index_to_remove[0])
    print(f"successfully removed playlist_id {remove_playlist.playlist_id}")


def _add_song_to_playlist(add_song_to_list: AddSongToPlaylist, mixtape: Dict[Any, Any]) -> None:
    """
    Add existing song to existing playlist
    :param add_song_to_list: Pydantic model that provide song_id and playlist_id
    :param mixtape: the data where the existing song and playlist reside
    :return: None
    """
    # if given song dose not exist in input file, print it and return
    existing_song_ids = {song["id"] for song in mixtape["songs"]}
    if add_song_to_list.song_id not in existing_song_ids:
        print(f"song_id {add_song_to_list.song_id} does not exist")
        return

    for playlist in mixtape["playlists"]:
        if playlist["id"] == add_song_to_list.playlist_id:
            if add_song_to_list.song_id in playlist["song_ids"]:
                print(f"song_id {add_song_to_list.song_id} is already in playlist_id {add_song_to_list.playlist_id}")
            else:
                playlist["song_ids"].append(add_song_to_list.song_id)
                print(f"successfully added song_id {add_song_to_list.song_id} "
                      f"to playlist_id {add_song_to_list.playlist_id}")
            return
    print(f"playlist_id {add_song_to_list.playlist_id} does not exist")


def main(args):
    try:
        with open(args.input_json) as mixtape_file:
            mixtape = json.load(mixtape_file)
        with open(args.changes_json) as changes_file:
            changes = json.load(changes_file)
    except FileNotFoundError as e:
        print(f"No such file or directory: {e.filename}")
        sys.exit(1)
    except Exception as e:
        print("Something is wrong with reading input files")
        sys.exit(1)

    for change in changes:
        if change["change_type"] == "add_new_playlist":
            _add_new_playlist(AddNewPlaylist(**change["change_detail"]), mixtape)
        elif change["change_type"] == "remove_playlist":
            _remove_playlist(RemovePlaylist(**change["change_detail"]), mixtape)
        elif change["change_type"] == "add_song_to_playlist":
            _add_song_to_playlist(AddSongToPlaylist(**change["change_detail"]), mixtape)
        else:
            print(f"change_type {change['change_type']} is not defined, ignored!")

    output = "output.json"
    with open(output, "w") as output_file:
        json.dump(mixtape, output_file, indent=4)

    print("done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File_processing arguments")
    parser.add_argument('-i', dest="input_json", default="mixtape.json",
                        help="Input json file mixtape.json")
    parser.add_argument('-c', dest="changes_json", default="changes.json",
                        help="Changes.json file")

    main(parser.parse_args())
