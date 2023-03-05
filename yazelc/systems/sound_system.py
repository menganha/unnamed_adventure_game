from yazelc import zesper
from yazelc.event.events import SoundTriggerEvent


class SoundSystem(zesper.Processor):

    def process(self):
        pass

    def on_sound_trigger(self, sound_trigger_event: SoundTriggerEvent):
        sound = self.world.resource_manager.get_sound(sound_trigger_event.id_str)
        sound.play()
