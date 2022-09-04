from yazelc.scenes.base_scene import BaseScene


def run_game_loop(initial_scene: BaseScene):
    current_scene = initial_scene
    running = True
    while running:
        current_scene.on_enter()
        current_scene.run()
        current_scene.on_exit()
        current_scene = current_scene.next_scene
        if not current_scene:
            running = False
