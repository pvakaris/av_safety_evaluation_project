## Information about diagram drawing

To draw the diagram look at the [draw_diagram_example.sh](./draw_diagram_example.sh).

**The list of all possible categories:**

```
      CollisionPenaltyPointsAverage
      LaneMarkingViolationPenaltyPointsAverage
      VehicleLightMisusePenaltyPointsAverage
      ProportionOfRouteCompletedAverage
      SpeedingPenaltyPointsAverage
      RoadTrafficViolationPenaltyPointsAverage
```
 - save_filename - specifies the name of the file that the diagram should be saved to. This file is an image.
 - title - specifies what shoudl be written at the top of the diagram
 - xlabel - x axis label
 - **data_filename** - points to the analysed data directory and then to either participants.xml or scenarios.xml. Please note, that at this moment, the diagrams can be drawn using only one of those two files and no other.