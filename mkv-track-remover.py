import os
import json
from pymkv import MKVFile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

class MKVTrackRemover:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)

    @staticmethod
    def load_config(path):
        with open(path, 'r') as file:
            config = json.load(file)
        return config

    def get_video_list(self):
        file_list = []
        for path in self.config["input_paths"]:
            if(os.path.isfile(path)):
                file_list.append(path)
            else:
                ext = self.config["file_extension"]
                for file in os.listdir(path):
                    if file.endswith(ext):
                        file_list.append(os.path.join(path, file))
        return file_list

    def remove_tracks_from_mkv(self, mkv, tracks_to_remove):
        for track in tracks_to_remove:
            mkv.remove_track(track.track_id)

    def filter_tracks(self, mkv):
        tracks_to_remove = []
        self.filter_audio_tracks(mkv, tracks_to_remove)
        self.filter_subtitle_tracks(mkv, tracks_to_remove)
        return tracks_to_remove
    
    def filter_audio_tracks(self, mkv, tracks_to_remove):
        audio_config = self.config["audio"]
        if not audio_config["enabled"]: 
            return
        audio_tracks = [track for track in mkv.tracks if track.track_type == 'audio']
        # If there is only one track, keep it
        if len(audio_tracks) == 1: 
            return
        for track in audio_tracks:
            if audio_config["keep_only_default"] and not track.default_track:
                tracks_to_remove.append(track)
            elif track.language not in audio_config["keep_languages"]:
                tracks_to_remove.append(track)
            elif audio_config["remove_commentary"] and self.track_is_commentary(track):
                tracks_to_remove.append(track)
    
    def track_is_commentary(self, track):
        return track.track_name is not None and "commentary" in track.track_name.lower()
    
    def filter_subtitle_tracks(self, mkv, tracks_to_remove):
        subtitle_config = self.config["subtitle"]
        if not subtitle_config["enabled"]: 
            return
        subtitle_tracks = [track for track in mkv.tracks if track.track_type == 'subtitles']
        # If there is only one track, keep it
        if len(subtitle_tracks) == 1: 
            return
        for track in subtitle_tracks:
            if track.language not in subtitle_config["keep_languages"]:
                mkv.remove_track(track.track_id)
    
    def mux_video(self, video_path):
        mkv = MKVFile(video_path)
        tracks_to_remove = self.filter_tracks(mkv)
        self.remove_tracks_from_mkv(mkv, tracks_to_remove)
        if self.config["file_suffix"]:
            path = Path(video_path)
            output_path = path.with_name(path.stem + self.config["file_suffix"] + path.suffix)
        else:
            print(f"Skipping: No file suffix specified in config file.")
            return
        mkv.mux(output_path)
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