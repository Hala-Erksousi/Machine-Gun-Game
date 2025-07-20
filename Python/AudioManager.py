from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QStackedWidget, QHBoxLayout, QShortcut, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal


from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist

class AudioManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AudioManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False 
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._load_sounds()
            self._initialized = True 

    def _create_player(self, file_path, volume=100, is_looping=False):
        player = QMediaPlayer()
        content = QMediaContent(QUrl.fromLocalFile(file_path))
        
        if is_looping:
            playlist = QMediaPlaylist()
            playlist.addMedia(content)
            playlist.setPlaybackMode(QMediaPlaylist.Loop)
            player.setPlaylist(playlist)
        else:
            player.setMedia(content)
            
        player.setVolume(volume)
        player.error.connect(lambda error_code, p=player: self.handle_player_error(error_code, p))
        return player

    def _load_sounds(self):
       
        self.countdown_player = self._create_player(r'.\\Sound\\robotic-countdown-43935.mp3', volume=70)
        self.result_player = self._create_player(r'.\\Sound\\marimba-win-b-2-209675.mp3', volume=60)
        self.game_over_player = self._create_player(r'.\\Sound\\End (online-audio-converter.com).mp3', volume=80)
        self.welcome_player = self._create_player(r'.\\Sound\\zapsplat_science_fiction_computer_voice_says_welcome_30843.mp3', volume=75)
        self.next_player_transition_sound = self._create_player(r'.\\Sound\\Next (online-audio-converter.com).mp3', volume=70)

    def handle_player_error(self, error_code, player):
        print(f"QMediaPlayer Error from {player.media().canonicalUrl().fileName()}: {error_code} - {player.errorString()}")
        if error_code == QMediaPlayer.ResourceError:
            print(f"Error Code: {error_code}. The media resource could not be resolved.")
        elif error_code == QMediaPlayer.FormatError:
            print(f"Error Code: {error_code}. The format of the media is not supported.")
        elif error_code == QMediaPlayer.NetworkError:
            print(f"Error Code: {error_code}. A network error occurred.")
        elif error_code == QMediaPlayer.AccessDeniedError:
            print(f"Error Code: {error_code}. Access to the media resource is denied.")
        QMessageBox.critical(None, "Sound Playback Error", 
                             f"Could not play sound: {player.media().canonicalUrl().fileName()}\n"
                             f"Error: {player.errorString()}")

    def play_countdown_sound(self):
        if self.countdown_player.state() == QMediaPlayer.PlayingState:
            self.countdown_player.setPosition(0)
        else:
            self.countdown_player.play()

    def play_result_sound(self):
        if self.result_player.state() == QMediaPlayer.PlayingState:
            self.result_player.setPosition(0)
        else:
            self.result_player.play()

    def play_game_over_sound(self):
        if self.game_over_player.state() == QMediaPlayer.PlayingState:
            self.game_over_player.setPosition(0)
        else:
            self.game_over_player.play() 

    def play_welcome_sound(self):
        if self.welcome_player.state() == QMediaPlayer.PlayingState:
            self.welcome_player.setPosition(0)
        else:
            self.welcome_player.play()
    def play_final_countdown_beep(self):
        pass

    def play_next_player_sound(self):
        if self.next_player_transition_sound:
            if self.next_player_transition_sound.state() == QMediaPlayer.PlayingState:
                self.next_player_transition_sound.setPosition(0) # Restart if already playing
            else:
                self.next_player_transition_sound.play()
        

    def stop_all_sounds(self):
        if self.countdown_player.state() == QMediaPlayer.PlayingState:
            self.countdown_player.stop()
        if self.result_player.state() == QMediaPlayer.PlayingState: 
            self.result_player.stop()
        if self.game_over_player.state() == QMediaPlayer.PlayingState: 
            self.game_over_player.stop()
        if self.welcome_player.state() == QMediaPlayer.PlayingState: 
            self.welcome_player.stop()
        if self.next_player_transition_sound and self.next_player_transition_sound.state() == QMediaPlayer.PlayingState:
            self.next_player_transition_sound.stop()
    
audio_manager = AudioManager()
