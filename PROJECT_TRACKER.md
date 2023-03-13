# Devlog (2023-03-13)

Big development: Sound system added. It is in its early stages but it does it job well. I've added more a more streamlined animation
inclusion
for enemies which should help also when designing other weapons.

I want to focus now on two main aspects. One would be to introduce the splash screen. The second would be to add a weapon that could be
used at a distance, probably the boomerang.

I'm doing everything a little dirty at the moment. There must be a moment where I will pick up and clean huge parts of the codebase. But
for now, it helps motivation-wise to keep doing things and looking at the results immediately. It definitely gives a sense of accomplishment
that helps me continue further.

# Devlog (2023-02-07)

I'm not sure what would be the best way to set up events. The main question is whether we should pass or not the world instance reference.
I have a problem with this because it couples the world with the event, and me no like it. The only alternative is to create an intermediate
event listener on a processor for example, that pases the reference to the world.

# Devlog (2023-02-05)

## New event system

Regarding the new event system. We treat now the input as an event which is then broadcast to all subscriber listeners. We can have one
listener, an Input system method, which loops over all entities with an "Input" component which just will have a callback for the event.
This is almost exactly as before, only that we have decouple the input event from the processor (somehow).

## How to deal with events triggered from events.

We will keep doing the same, i.e., we copy the event queue, process it. Then query if the event queue has new elements, which we will
process. We keep doing this process iteratively until there's no more queue events.

## How to deal with events triggers that need to be delayed.

Establish dictionary of events, with the event type as key and the delay in frames as the value. On each frame a system
(script/event system) takes care of reducing the delay by one, and if it's zero then it add the events to the main queue.

## Events with many target entities/no target entities/one target entity

We can divide the types of event according to the treatment on the three categories of the above title.

* Events with many target entities: For this we create a single callback method on a processor. The point is that when it affects entities,
  these can be, e.g., already erased by the time the event is called. Therefore, we need to couple these with the ECS World. On the method
  we either
    1. If the event carries the affected entities, and the handling doesn't care which ones (perhaps only in the general sense: _does
       entity a have a particular component?_. then we simply process it. In the collision case, we just handle the two entities that are
       part of the event message, and we do operations on them (possibly adding new events to the queue)
    2. If the event is general (like in the input case). We loop over the entities that have a corresponding component, that could be a
       callback on the event for example.
* Event with no target entities: We don't have to deal with ECS in this case, only in the high level sense. The events are handled by simple
  defined at the scene level so that they keep references and are not automatically removed from the subscriber list. Examples: Death,
  Pause, etc.
* Events with one particular target entity: This is the case of scripts. Not that commonly used. We could in principle deal with these
  just like in the previous case. Create a handler to a particular callback and make them subscribe and live on the high level

# Planned tasks by priority

* Implement text box system for use in, e.g., NPC dialogues, signs
* Fix player sprite: assure that is bound to the 16x16 base tile dimension and the sword attack range is equal in all directions
* Fix issue with doors: a) Make the point of contact lower (as of now you have to go certain offset to trigger the transition) and b) make
  them solid for other entities
* Implement transition animation.
* Make a special scene type just for dungeons with its own systems and items
    * Switch that trigger door openings (killing all enemies, pressing a switch)
    * Key/locked door system
* event_manager should be passed to all the process method of the systems. The decision to make it a global variable is dangerous
