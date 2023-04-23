""" This is the finite State Machine manager """

from yazelc.scenes.base_scene import BaseScene


def run_game_loop(initial_scene: BaseScene):
    current_scene = initial_scene
    while current_scene is not None:
        current_scene.on_enter()
        while not current_scene.finished:
            current_scene.update()
        current_scene.on_exit()
        current_scene.event_manager.remove_all_handlers()  # TODO: Should this part of the scene code?
        current_scene = current_scene.next_scene
