import carla
import random
import numpy as np
import logging

logger= logging.getLogger(__name__)


class Scenario():
    
    def __init__(self, parameters, path_details, seed):
        self.scenario_parameters = parameters
        self.path_details = path_details
        # Used for reproducable randomizarion
        self.seed = seed
        
        self.vehicles_list = []
        self.walkers_list = []
        self.two_wheel_vehicles_list = []
        self.all_id = []
        self.all_actors = []
        
        self.traffic_manager = None
        self.synchronous_master = False
        self.world = None    
        self.populated = False
        
        self.walker_speed = None
    
    def spawn(self, client):
        logger.info("Spawning the scenario actors")
        try:
            blueprints_vehicles_all = get_actor_blueprints(self.world, "vehicle.*", "All")
            
            blueprints_vehicles = get_safe_vehicle_blueprints(blueprints_vehicles_all)
            blueprints_walkers = get_actor_blueprints(self.world, "walker.pedestrian.*", "2")
            blueprints_two_wheel_vehicles = get_two_wheel_vehicle_blueprints(blueprints_vehicles_all)
        except Exception as e:
            logger.error("An error occured trying to get the blueprints", exc_info=True)
            raise e
        
        
        try:
            # Read all the parameters from the scenario object
            parameters = self.scenario_parameters
            number_of_pedestrians = int(parameters["number_of_pedestrians"])
            number_of_vehicles = int(parameters["number_of_vehicles"])
            number_of_two_wheel_vehicles = int(parameters["number_of_two_wheel_vehicles"])
            proportion_of_speeding_vehicles = float(parameters["proportion_of_speeding_vehicles"])
            proportion_of_vehicles_without_lights = float(parameters["proportion_of_vehicles_without_lights"])
            proportion_of_light_ignoring_vehicles = float(parameters["proportion_of_light_ignoring_vehicles"])
            light_ignoring_percent = float(parameters["light_ignoring_percent"])
            proportion_of_sign_ignoring_vehicles = float(parameters["proportion_of_sign_ignoring_vehicles"])
            sign_ignoring_percent = float(parameters["sign_ignoring_percent"])
            proportion_of_vehicle_ignoring_vehicles = float(parameters["proportion_of_vehicle_ignoring_vehicles"])
            vehicle_ignoring_percent = float(parameters["vehicle_ignoring_percent"])
            proportion_of_walker_ignoring_vehicles = float(parameters["proportion_of_walker_ignoring_vehicles"])
            walker_ignoring_percent = float(parameters["walker_ignoring_percent"])
            proportion_of_keeping_right_vehicles = float(parameters["proportion_of_keeping_right_vehicles"])
            keeping_right_percent = float(parameters["keeping_right_percent"])
            proportion_of_lane_changing_vehicles = float(parameters["proportion_of_lane_changing_vehicles"])
            lane_change_percent = float(parameters["lane_change_percent"])
            proportion_of_misbehaving_pedestrians = float(parameters["proportion_of_misbehaving_pedestrians"])
            proportion_of_running_pedestrians = float(parameters["proportion_of_running_pedestrians"])
            proportion_of_road_crossing_pedestrians = float(parameters["proportion_of_road_crossing_pedestrians"])
        except Exception as e:
            logger.error("An error occured trying to get retrieve scenario parameters", exc_info=True)
            raise e
        
        
        # ALL NECCESSARY PARAMETERS WERE EXTRACTED
        
        try:
            SpawnActor = carla.command.SpawnActor
            SetAutopilot = carla.command.SetAutopilot
            FutureActor = carla.command.FutureActor

            start = self.path_details["start_location"]
            hero_spawn_location = carla.Location(x=float(start["x"]), y=float(start["y"]), z=float(start["z"]))
            
            # Removes ones too close to the player's spawn location
            spawn_points = self.world.get_map().get_spawn_points()
            spawn_points = filter_spawn_points(spawn_points, hero_spawn_location, 5)
            number_of_spawn_points = len(spawn_points)

            total_number_of_vehicles = (number_of_vehicles + number_of_two_wheel_vehicles)
            if total_number_of_vehicles <= number_of_spawn_points:
                random.shuffle(spawn_points)
    
            else:
                logger.warning("There are too many vehicles for too few spawn points. Reducing the number of vehicles. There are {} spawn points for vehicles in total.".format(number_of_spawn_points))
                difference = total_number_of_vehicles - number_of_spawn_points
                if (number_of_vehicles - difference) >= 0:
                    number_of_vehicles = (number_of_vehicles - difference)
                else:
                    # Over is going to be negative
                    over = (number_of_vehicles - difference)
                    number_of_two_wheel_vehicles = number_of_two_wheel_vehicles + over
                    
            total_number_of_vehicles = (number_of_vehicles + number_of_two_wheel_vehicles)        
            vehicle_spawn_points, two_wheel_vehicle_spawn_points = divide_list(spawn_points, number_of_vehicles, number_of_two_wheel_vehicles)
            
            # Make all vehicles aim for the speed limit
            self.traffic_manager.global_percentage_speed_difference(0)
        except Exception as e:
            logger.error("An error occured trying to get the spawn points", exc_info=True)
            raise e
        
        try:
            # --------------
            # Spawn vehicles
            # --------------
            batch = []
            for n, transform in enumerate(vehicle_spawn_points):
                if n >= number_of_vehicles:
                    break
                blueprint = random.choice(blueprints_vehicles)
                if blueprint.has_attribute('color'):
                    color = random.choice(blueprint.get_attribute('color').recommended_values)
                    blueprint.set_attribute('color', color)
                if blueprint.has_attribute('driver_id'):
                    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                    blueprint.set_attribute('driver_id', driver_id)
                blueprint.set_attribute('role_name', 'autopilot')
                # Spawn the cars and set their autopilot and light state all together
                batch.append(SpawnActor(blueprint, transform)
                    .then(SetAutopilot(FutureActor, False, self.traffic_manager.get_port())))

            for response in client.apply_batch_sync(batch, self.synchronous_master):
                if response.error:
                    logger.error(response.error)
                else:
                    self.vehicles_list.append(response.actor_id)
                    
            logger.info("The {}/{} vehicles were successfully spawned".format(len(self.vehicles_list), number_of_vehicles))
        
        except Exception as e:
            logger.error("Error creating vehicles on the map.", exc_info=True)
            raise e
            
        try:    
            # --------------
            # Spawn two-wheel vehicles
            # --------------
            batch = []
            for n, transform in enumerate(two_wheel_vehicle_spawn_points):
                if n >= number_of_two_wheel_vehicles:
                    break
                blueprint = random.choice(blueprints_two_wheel_vehicles)
                if blueprint.has_attribute('color'):
                    color = random.choice(blueprint.get_attribute('color').recommended_values)
                    blueprint.set_attribute('color', color)
                if blueprint.has_attribute('driver_id'):
                    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                    blueprint.set_attribute('driver_id', driver_id)
                blueprint.set_attribute('role_name', 'autopilot')
                # Spawn the cars and set their autopilot and light state all together
                batch.append(SpawnActor(blueprint, transform)
                    .then(SetAutopilot(FutureActor, False, self.traffic_manager.get_port())))

            for response in client.apply_batch_sync(batch, self.synchronous_master):
                if response.error:
                    logger.error(response.error)
                else:
                    self.two_wheel_vehicles_list.append(response.actor_id)
                    
            logger.info("The {}/{} two-wheel vehicles were successfully spawned".format(len(self.two_wheel_vehicles_list), number_of_two_wheel_vehicles))
        
                
        except Exception as e:
            logger.error("Error creating two-wheel vehicles on the map.", exc_info=True)
            raise e
        
        try:
            logger.info("Setting the vehicle behavior according to the scenario parameters")
            ### SETUP VEHICLE BEHAVIOUR
                
            all_vehicles = self.vehicles_list + self.two_wheel_vehicles_list
            amount_vehicles = len(all_vehicles)
            all_vehicle_actors = self.world.get_actors(all_vehicles)
                   

            # Distance 
            for actor in all_vehicle_actors:
                # Select a distance to keep between 1 and 5 metres randomly.
                diff = random.randint(1, 5)
                self.traffic_manager.auto_lane_change(actor, True)
                self.traffic_manager.distance_to_leading_vehicle(actor, diff)
                
            # Set not update vehicle lights for certain vehicles
            amount_of = int(np.round(amount_vehicles * proportion_of_vehicles_without_lights))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                self.traffic_manager.update_vehicle_lights(actor, False)
                
            # Update the lights for the rest
            for v in all_vehicles:
                if(v not in random_vehicles):
                    actor = self.world.get_actor(v)
                    self.traffic_manager.update_vehicle_lights(actor, True)
                
                
            # Speeding    
            amount_of = int(np.round(amount_vehicles * proportion_of_speeding_vehicles))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                # Select a speeding increase randomly
                diff = random.randint(-30, -1)
                self.traffic_manager.vehicle_percentage_speed_difference(actor, diff)
   
            # Light ignoring    
            amount_of = int(np.round(amount_vehicles * proportion_of_light_ignoring_vehicles))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                self.traffic_manager.ignore_lights_percentage(actor, light_ignoring_percent)
          
            # Sign ignoring    
            amount_of = int(np.round(amount_vehicles * proportion_of_sign_ignoring_vehicles))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                self.traffic_manager.ignore_signs_percentage(actor, sign_ignoring_percent)
                
            # Vehicle ignoring    
            amount_of = int(np.round(amount_vehicles * proportion_of_vehicle_ignoring_vehicles))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                self.traffic_manager.ignore_vehicles_percentage(actor, vehicle_ignoring_percent)
                
            # Walker ignoring    
            amount_of = int(np.round(amount_vehicles * proportion_of_walker_ignoring_vehicles))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                self.traffic_manager.ignore_walkers_percentage(actor, walker_ignoring_percent)
                
            # Keep right rule    
            amount_of = int(np.round(amount_vehicles * proportion_of_keeping_right_vehicles))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                self.traffic_manager.keep_right_rule_percentage(actor, keeping_right_percent)
                
            # Lane changing left    
            amount_of = int(np.round(amount_vehicles * proportion_of_lane_changing_vehicles))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                self.traffic_manager.random_left_lanechange_percentage(actor, lane_change_percent)
                
            # Lane changing right    
            amount_of = int(np.round(amount_vehicles * proportion_of_lane_changing_vehicles))
            random_vehicles = random.sample(all_vehicles, amount_of)
            for v in random_vehicles:
                actor = self.world.get_actor(v)
                self.traffic_manager.random_right_lanechange_percentage(actor, lane_change_percent) 
                
            logger.info("The behaviour of vehicles was successfully set")
        
        except Exception as e:
            logger.error("Error setting the behaviour of vehicles.", exc_info=True)
            raise e
        
        
        try:
            # -------------
            # Spawn Walkers
            # -------------
            # Random locations to spawn
            
            number_of_pedestrians_initial = number_of_pedestrians
            
            try:
                spawn_points = []
                for i in range(number_of_pedestrians):
                    spawn_point = carla.Transform()
                    loc = self.world.get_random_location_from_navigation()
                    if (loc != None):
                        spawn_point.location = loc
                        spawn_points.append(spawn_point)    
                
                if(len(spawn_points) >= number_of_pedestrians):
                    logger.debug("There is a required amount of spawn points for pedestrians on the map.")
                else:
                    number_of_pedestrians = len(spawn_points)
            except Exception as e:
                logger.error(e)
                
            # Spawn walker objects
            walker_speed = []
            walker_speed2 = []
            logger.debug("Need to spawn {} pedestrians".format(number_of_pedestrians))
            for i in range(number_of_pedestrians):
                
                # Modify the blueprint
                walker_bp = random.choice(blueprints_walkers)
                # set as not invincible
                if walker_bp.has_attribute('is_invincible'):
                    walker_bp.set_attribute('is_invincible', 'false')
                # set the max speed
                if walker_bp.has_attribute('speed'):
                    if (random.random() > proportion_of_running_pedestrians):
                        # walking
                        walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
                    else:
                        # running
                        walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
                else:
                    walker_speed.append(0.0)
                
                logger.debug("The blueprint was set.")
                try:
                    # Try to spawn the pedestrian 10000 times and
                    y = 0
                    not_spawned = True
                    while(not_spawned and y < 10000):
                        spawn_point = carla.Transform()
                        loc = self.world.get_random_location_from_navigation()
                        if (loc != None):
                            spawn_point.location = loc
                            batch = []
                            batch.append(SpawnActor(walker_bp, spawn_point))
                            results = client.apply_batch_sync(batch, True)
                            if results[0].error:
                                logger.debug(results[0].error)
                                y += 1
                            else:
                                not_spawned = False
                                self.walkers_list.append({"id": results[0].actor_id})
                                walker_speed2.append(walker_speed[i])
                                break
                        else:
                            y += 1
                except Exception as e:
                    logger.error(e)
                logger.debug("There were {} respawns for this walker".format(y)) 
                
            
            logger.info("Successfully spawned {}/{} walkers.".format(len(self.walkers_list), number_of_pedestrians_initial))
            self.walker_speed = walker_speed2
            
            # Spawn the walker controller
            batch = []
            walker_controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')
            for i in range(len(self.walkers_list)):
                batch.append(SpawnActor(walker_controller_bp, carla.Transform(), self.walkers_list[i]["id"]))
            results = client.apply_batch_sync(batch, True)
            for i in range(len(results)):
                if results[i].error:
                    logger.error(results[i].error)
                else:
                    self.walkers_list[i]["con"] = results[i].actor_id
                    
            # Put together the walkers and controllers id to get the objects from their id
            for i in range(len(self.walkers_list)):
                self.all_id.append(self.walkers_list[i]["con"])
                self.all_id.append(self.walkers_list[i]["id"])
            self.all_actors = self.world.get_actors(self.all_id)
        
        except Exception as e:
            logger.error("Error creating walkers on the map.", exc_info=True)
            raise e

        self.world.tick()
        self.world.set_pedestrians_cross_factor(proportion_of_road_crossing_pedestrians)
        self.populated = True
    
    # Setup the traffic manager and other parameters before the simulation
    def setup(self, traffic_manager, world):
        logger.info("Setting up the scenario")
        self.traffic_manager = traffic_manager
        self.world = world
        self.traffic_manager.set_global_distance_to_leading_vehicle(2.5)
        self.traffic_manager.set_random_device_seed(self.seed)
        self.world.set_pedestrians_seed(self.seed)
        random.seed(self.seed)
        self.traffic_manager.set_hybrid_physics_mode(True)
        self.traffic_manager.set_hybrid_physics_radius(70.0)
        
        settings = self.world.get_settings()
        self.traffic_manager.set_synchronous_mode(True)
        if not settings.synchronous_mode:
            self.synchronous_master = True
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05
        else:
            self.synchronous_master = False
    
    # Unfreeze all actors and let them move as specified
    def start(self):
        logger.info("Unfreezing all actors in the simulation.")
        port = self.traffic_manager.get_port() 
        
        # Unfreeze vehicles
        for v in self.vehicles_list:
            actor = self.world.get_actor(v)
            actor.set_autopilot(True, port)
        
        # Unfreeze two-wheel vehicles
        for b in self.two_wheel_vehicles_list:
            actor = self.world.get_actor(b)
            actor.set_autopilot(True, port)

        # Unfreeze walkers
        for i in range(0, len(self.all_id), 2):
            self.all_actors[i].start()
            self.all_actors[i].go_to_location(self.world.get_random_location_from_navigation())
            self.all_actors[i].set_max_speed(float(self.walker_speed[int(i/2)]))
    
    # Change settings back to default and destroy all actors
    def finish(self, client):
        logger.info("Finishing the scenario")
        if self.synchronous_master:
            settings = self.world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = None
            self.world.apply_settings(settings)

        logger.info('Destroying {} vehicles'.format(len(self.vehicles_list)))
        client.apply_batch([carla.command.DestroyActor(x) for x in self.vehicles_list])
        
        logger.info('Destroying {} two-wheel vehicles'.format(len(self.two_wheel_vehicles_list)))
        client.apply_batch([carla.command.DestroyActor(x) for x in self.two_wheel_vehicles_list])
        # Stop walker controllers (list is [controller, actor, controller, actor ...])
        for i in range(0, len(self.all_id), 2):
            self.all_actors[i].stop()
        logger.info('Destroying {} walkers'.format(len(self.walkers_list)))
        client.apply_batch([carla.command.DestroyActor(x) for x in self.all_id])
        
        self.populated = False
    
    
def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)
    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps
    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            logger.warning("Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        logger.warning("Actor Generation is not valid. No actor will be spawned.")
        return []
    
def get_safe_vehicle_blueprints(blueprints):
    blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
    blueprints = [x for x in blueprints if not x.id.endswith('microlino')]
    blueprints = [x for x in blueprints if not x.id.endswith('carlacola')]
    blueprints = [x for x in blueprints if not x.id.endswith('cbertruck')]
    blueprints = [x for x in blueprints if not x.id.endswith('t2')]
    blueprints = [x for x in blueprints if not x.id.endswith('sprinter')]
    blueprints = [x for x in blueprints if not x.id.endswith('firetruck')]
    blueprints = [x for x in blueprints if not x.id.endswith('ambulance')]
    blueprints = sorted(blueprints, key=lambda bp: bp.id)
    return blueprints
    
def get_two_wheel_vehicle_blueprints(blueprints):
    return [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 2]

def distanceBetweenTwoLocations(start, finish):
    first = np.array((start.x, start.y))
    second = np.array((finish.x, finish.y))
    return np.linalg.norm(first-second)

def filter_spawn_points(spawn_points, hero_spawn_location, min_distance):
    try:
        filtered_spawn_points = []
        for point in spawn_points:
            distance = distanceBetweenTwoLocations(point.location, hero_spawn_location)
            # If the spawn location is further than two metres from the player's location, add to the filtered ones
            if distance > min_distance:
                filtered_spawn_points.append(point)
        return filtered_spawn_points
    except Exception as e:
        logger.error(e)
        
def divide_list(input_list, x, y):
    first_list = input_list[:x]
    second_list = input_list[x:x+y]
    return first_list, second_list