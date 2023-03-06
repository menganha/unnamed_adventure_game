from yazelc import zesper
from yazelc.event.events import SoundTriggerEvent, SoundEndEvent


class SoundSystem(zesper.Processor):

    def process(self):
        pass

    def on_sound_trigger(self, sound_trigger_event: SoundTriggerEvent):
        sound = self.world.resource_manager.get_sound(sound_trigger_event.id_str)
        sound.play()

    def on_sound_end(self, sound_end_event: SoundEndEvent):
        sound = self.world.resource_manager.get_sound(sound_end_event.id_str)
        sound.stop()
