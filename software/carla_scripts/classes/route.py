from config import FINISH_DISTANCE_FROM_WAYPOINT, DISTANCE_FROM_WAYPOINT, DISTANCE_FROM_WAYPOINT_CHANGING_LANE
from classes.helpers import distanceBetweenTwoLocations

class Route():
    
    def __init__(self, waypoints):
        self.routepoints = []
        for waypoint in waypoints:
            self.routepoints.append((waypoint, 0))
        # Last routepoint is out finish point
        self.finish_lane_waypoints = self.get_finish_lane_waypoints(waypoints[len(waypoints) - 1][0])

    
    def get_finish_lane_waypoints(self, waypoint):
        return [*self.getAllLeftWaypointsRecursively(waypoint, [], 0), *self.getAllRightWaypointsRecursively(waypoint, [], 0), waypoint]
    
    # Return percent of route completed
    def get_route_completion(self):
        length = len(self.routepoints)
        completed = sum(x[1] for x in self.routepoints)
        return '%.2f' % (completed / length)
    
    # Get shortest distance comparing each waypoint in waypoints
    # with the provided location
    def get_shortest_distance(self, location):
        shortest_distance = None
        for routepoint in self.routepoints:
            waypoint_location = routepoint[0][0].transform.location
            distance = distanceBetweenTwoLocations(location, waypoint_location)
            if shortest_distance is None or distance < shortest_distance:
                shortest_distance = distance
        return shortest_distance
    
    # Return true if the last location on route was reached
    def is_finished(self, player_location):
        for waypoint in self.finish_lane_waypoints:
            distance = distanceBetweenTwoLocations(player_location, waypoint.transform.location)
            if distance <= FINISH_DISTANCE_FROM_WAYPOINT:
                return True
        return False
    
    # Marks the routepoints (x, 1) if the routepoint's distance is <= DISTANCE_FROM_WAYPOINT
    def recalculate(self, location):
        for i in range(len(self.routepoints)):
            routepoint = self.routepoints[i]
            waypoint_location = routepoint[0][0].transform.location
            distance = distanceBetweenTwoLocations(location, waypoint_location)
            if distance <= DISTANCE_FROM_WAYPOINT:
                waypoint = routepoint[0]
                self.routepoints.pop(i)
                self.routepoints.append((waypoint, 1))
                
        # print("Completed: " + str(self.get_completage()))
        
    ###          ADVANCED STUFF
        
    # Marks the routepoints (x, 1) if the routepoint's distance is <= DISTANCE_FROM_WAYPOINT
    def advanced_recalculate(self, location, is_changing_lane):
        for i in range(len(self.routepoints)):
            routepoint = self.routepoints[i]
            waypoint = routepoint[0]
            left_waypoints = self.getLeftValidWaypointsRecursively(waypoint[0], [], 0)
            right_waypoints = self.getRightValidWaypointsRecursively(waypoint[0], [], 0)
            waypoints = [*left_waypoints, *right_waypoints, waypoint[0]]
            for w in waypoints:
                distance = distanceBetweenTwoLocations(location, w.transform.location)
                if is_changing_lane:
                    if distance <= DISTANCE_FROM_WAYPOINT:
                        self.routepoints.pop(i)
                        self.routepoints.append((waypoint, 1))
                else:
                    if distance <= DISTANCE_FROM_WAYPOINT_CHANGING_LANE:
                        self.routepoints.pop(i)
                        self.routepoints.append((waypoint, 1))
        # print("Completed: " + str(self.get_completage()))
                
    def get_all_waypoints(self):
        waypoints = []
        for routepoint in self.routepoints:
            waypoint = routepoint[0][0]
            waypoints.append(waypoint)
            for w in self.getLeftValidWaypointsRecursively(waypoint, [], 0):
                waypoints.append(w)
            for w in self.getRightValidWaypointsRecursively(waypoint, [], 0):
                waypoints.append(w)
        return waypoints
    
    # Get all lanes on the current road (to the left of the waypoint) that are valid drive for the vehicle driving this route.
    def getLeftValidWaypointsRecursively(self, waypoint, list, recursive_calls):
        if waypoint == None or recursive_calls > 8:
            return list
        lane_change = waypoint.lane_change
        if str(lane_change) == "Left" or str(lane_change) == "Both":
            left_lane_waypoint = waypoint.get_left_lane()
            if left_lane_waypoint == None:
                return list
            list.append(left_lane_waypoint)
            recursive_calls += 1
            return self.getLeftValidWaypointsRecursively(left_lane_waypoint, list, recursive_calls)
        else:
            return list
    
    # Get all road lanes on the map to the left of the current lane. Primarily used when marking the finish line.
    def getAllLeftWaypointsRecursively(self, waypoint, list, recursive_calls):
        left_lane_waypoint = waypoint.get_left_lane()
        if left_lane_waypoint is not None:
            list.append(left_lane_waypoint)
            recursive_calls += 1
            return self.getLeftValidWaypointsRecursively(left_lane_waypoint, list, recursive_calls)
        else:
            return list
    
    # Get all lanes on the current road (to the right of the waypoint) that are valid drive for the vehicle driving this route.
    def getRightValidWaypointsRecursively(self, waypoint, list, recursive_calls):
        if waypoint == None or recursive_calls > 8:
            return list
        lane_change = waypoint.lane_change
        if str(lane_change) == "Right" or str(lane_change) == "Both":
            right_lane_waypoint = waypoint.get_right_lane()
            if right_lane_waypoint == None:
                return list
            list.append(right_lane_waypoint)
            recursive_calls += 1
            return self.getRightValidWaypointsRecursively(right_lane_waypoint, list, recursive_calls)
        else:
            return list
    
    # Get all road lanes on the map to the right of the current lane. Primarily used when marking the finish line.
    def getAllRightWaypointsRecursively(self, waypoint, list, recursive_calls):
        right_lane_waypoint = waypoint.get_right_lane()
        if right_lane_waypoint is not None:
            list.append(right_lane_waypoint)
            recursive_calls += 1
            return self.getRightValidWaypointsRecursively(right_lane_waypoint, list, recursive_calls)
        else:
            return list