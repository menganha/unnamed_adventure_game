# Design and project planning document

## List of tasks to do

- [ ] Clean Code
    - [ ] Clean Hitboxes code
    - [ ] Change Player class to be a dirty sprite
    - [ ] Separate the interface between control and the player
- [X] Introduce cooldown time for player
- [ ] Introduce better AI for enemies
    - [ ] path finding, i.e., to look for you when they see you.
    - [ ] Either stop or recoil when they hit the player to prevent an enemy to constantly make damage.
- [ ] Improve the movement, i.e., introduce a threshold between player and solids hitboxes so that the player "smothly" gets pushed away from the obstacle.
    - [ ] Introduce smooth sliding when touching world obstacle
- [ ] Introduce UI with health, items, etc. This will involve changing the current size of the playable screen and posibly entering some conditions for not redrawing the UI while is not changing.
    - [X] Introduce Life
    - [ ] Introduce Items
    - [ ] Introduce Currency
- [ ] Improve Sprite Images
    - [ ] Introduce death animation (I'm looking something like ninja gaiden)
- [ ] Introduce dungeon entering logic, i.e., what tiles do load another set of maps.
- [ ] Introduce text system for reading signs.
- [ ] Introduce layering in map tiles so that player can be drawn between layers, e.g., under the leaves of a tall tree.
- [ ] Introduce Big Boss.
- [ ] Introduce Item picking in, e.g., chests, on the floor leaved by enemies
    - [ ] Introduce new weapons
    - [ ] Introduce currency
- [ ] Designs at least one dungeon.

## Some details to be aware of

- Enemies hitboxes default to the sprite size of the animation. This is automatic and therefor quite nice. To be more flexible think about defining the hitbox size independently.

## Current Issues

- [ ] UI Background is not configurable and defaults to black
- [X] Change of hearts from 1 to 0.5 is not rendered. Change the hearts to be an integer number, i.e., 2*actual number
