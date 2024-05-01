import os
import json
from pymkv import MKVFile
from concurrent.futures import ThreadPoolExecutor

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
        input_path = self.config["input_path"]
        ext = self.config["file_extension"]
        for file in os.listdir(input_path):
            if file.endswith(ext):
                file_list.append(os.path.join(input_path, file))
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
        audio_tracks = [track for track in mkv.tracks if track.track_type == 'audio']
        # If there is only one track, keep it
        if len(audio_tracks) == 1: 
            return
        for track in audio_tracks:
            if ((self.config["audio"]["keep_only_default"] and not track.default_track) 
                or (track.language not in self.config["audio"]["keep_languages"])
                or (self.config["audio"]["remove_commentary"] and track.track_is_commentary())):
                tracks_to_remove.append(track)

    def track_is_commentary(self, track):
        return "commentary" in track.track_name.lower()
    
    def filter_subtitle_tracks(self, mkv, tracks_to_remove):
        if not self.config["subtitle"]["enabled"]: 
            return
        subtitle_config = self.config["subtitle"]
        subtitle_tracks = [track for track in mkv.tracks if track.track_type == 'subtitles']
        # If there is only one track, keep it
        if len(subtitle_tracks) == 1: 
            return
        for track in subtitle_tracks:
            if track.language not in self.config["subtitle"]["keep_languages"]:
                mkv.remove_track(track.track_id)
    
    def mux_video(self, video_path):
        mkv = MKVFile(video_path)
        tracks_to_remove = self.filter_tracks(mkv)
        self.remove_tracks_from_mkv(mkv, tracks_to_remove)
        output_path = video_path.replace(self.config["input_path"], self.config["input_path"] + self.config["path_suffix"])
        mkv.mux(output_path)
        print(f'Muxed and saved: {output_path}')

    def process_all_videos(self):
        videos = self.get_video_list()
        with ThreadPoolExecutor() as executor:
            for video in videos:
                executor.submit(self.mux_video, video)

if __name__ == "__main__":
    remover = MKVTrackRemover('config.json')
    remover.process_all_videos()


# def list_mkv_tracks(video_path):
#     mkv = MKVFile(video_path)
#     print(f'Tracks in {video_path}:')
#     for track in mkv.tracks:
#         print(track)

# list_mkv_tracks("Z:/TV Series/Train.to.the.End.of.the.World\[Nekomoe kissaten&LoliHouse] Shuumatsu Train Doko e Iku - 04 [WebRip 1080p HEVC-10bit AAC ASSx2].mkv")