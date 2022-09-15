from yazelc import zesper
from yazelc.camera import Camera


class CameraSystem(zesper.Processor):
    """
    Updates the camera entity to center around the input entity position
    """

    def __init__(self, camera: Camera):
        super().__init__()
        self.camera = camera

    def process(self):
        self.camera.update(self.world)
