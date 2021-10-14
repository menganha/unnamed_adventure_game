import components as cmp
import entity_fabric as fabric
import systems as sys
from config import Config
from maps import Maps
from scene import Scene


class OverWorldScene(Scene):

    def on_enter(self):
        player_ent = fabric.create_player_at(x_pos=350, y_pos=370, world=self.world)

        # Add map entity
        map_entity = self.world.create_entity()
        overworld_map = Maps('data/overworld_map.tmx')
        map_surface = overworld_map.create_map_image()
        self.world.add_component(map_entity, cmp.Position(x=0, y=0))
        self.world.add_component(map_entity, cmp.Renderable(image=map_surface, depth=3))
        for position, hitbox in overworld_map.create_solid_rectangles():
            self.world.create_entity(position, hitbox)

        # Add camera entity
        camera_entity = self.world.create_entity()
        self.world.add_component(camera_entity, cmp.Position(x=0, y=0))

        # Create enemy
        fabric.create_jelly_at(400, 400, self.world)

        # Create some Processor instances, and assign them to be processed.
        input_processor = sys.InputSystem()
        physics_system = sys.PhysicsSystem()
        render_processor = sys.RenderSystem(window=self.window, camera_entity=camera_entity)
        animation_system = sys.AnimationSystem()
        movement_processor = sys.MovementSystem(min_x=0, max_x=Config.RESOLUTION[0],
                                                min_y=0, max_y=Config.RESOLUTION[1])
        camera_processor = sys.CameraSystem(camera_entity, entity_followed=player_ent)
        combat_system = sys.CombatSystem(player_entity=player_ent)
        self.world.add_processor(input_processor)
        self.world.add_processor(animation_system)
        self.world.add_processor(combat_system)
        self.world.add_processor(movement_processor)
        self.world.add_processor(physics_system)
        self.world.add_processor(camera_processor)
        self.world.add_processor(render_processor)

    def on_exit(self):
        pass
