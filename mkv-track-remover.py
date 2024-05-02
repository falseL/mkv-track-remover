import json
from pathlib import Path
from pymkv import MKVFile
from concurrent.futures import ThreadPoolExecutor

class MKVTrackRemover:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.validate_config()

    @staticmethod
    def load_config(path):
        with open(path, 'r') as file:
            config = json.load(file)
        return config
    
    def validate_config(self):
        required_keys = ["input_paths", "file_extension", "audio", "subtitle", "enable_threading"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Configuration key '{key}' not found.")

    def get_video_list(self):
        file_list = []
        for path in self.config["input_paths"]:
            path_obj = Path(path)
            if path_obj.is_file():
                file_list.append(path)
            elif path_obj.is_dir():
                file_list.extend(path_obj.glob(f'*.{self.config["file_extension"]}'))
        return file_list

    def filter_tracks(self, mkv):
        tracks_to_remove = []
        self.filter_audio_tracks(mkv, tracks_to_remove)
        self.filter_subtitle_tracks(mkv, tracks_to_remove)
        tracks_to_remove_ids = [track.track_id for track in tracks_to_remove]
        # Sort in descending order to avoid issues with track removal
        tracks_to_remove_ids_sorted_desc = sorted(tracks_to_remove_ids, reverse=True)
        return tracks_to_remove_ids_sorted_desc

    def filter_audio_tracks(self, mkv, tracks_to_remove):
        if not self.config["audio"]["enabled"]:
            return
        for track in mkv.tracks:
            if track.track_type == 'audio' and (
                (self.config["audio"]["keep_only_default"] and not track.default_track) or
                (track.language not in self.config["audio"]["keep_languages"]) or
                (self.config["audio"]["remove_commentary"] and "commentary" in (track.track_name or "").lower())
            ):
                tracks_to_remove.append(track)

    def filter_subtitle_tracks(self, mkv, tracks_to_remove):
        if not self.config["subtitle"]["enabled"]:
            return
        for track in mkv.tracks:
            if track.track_type == 'subtitles' and track.language not in self.config["subtitle"]["keep_languages"]:
                tracks_to_remove.append(track)

    def mux_video(self, video_path):
        try:
            mkv = MKVFile(video_path)
            tracks_to_remove = self.filter_tracks(mkv)
            for track_id in tracks_to_remove:
                mkv.remove_track(track_id)
            output_path = Path(video_path).with_suffix(self.config.get("file_suffix", "") + ".mkv")
            mkv.mux(output_path)
        except Exception as e:
            print(f'Error processing {video_path}: {e}')
            return
        print(f'Muxed and saved: {output_path}')

    def process_all_videos(self):
        videos = self.get_video_list()
        if self.config["enable_threading"]:
            with ThreadPoolExecutor() as executor:
                for video in videos:
                    executor.submit(self.mux_video, video)
        else:
            for video in videos:
                self.mux_video(video)

if __name__ == "__main__":
    remover = MKVTrackRemover('config.json')
    remover.process_all_videos()
    input("Press any key to exit...")