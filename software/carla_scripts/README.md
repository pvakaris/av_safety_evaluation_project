## About the simulations

To run the simulations, your machine must meet the software requirements stated in the [README.md](../../README.md) file in the software directory.

Launch the UE4 engine running CARLA server following the guide in CARLA's [documentation](https://carla.readthedocs.io/en/latest/).

```
bash run.sh [participant's name e.g. wilson]
```
This will run n scenarios sequentially, as stated in the [scenario_list.json](./scenario_list.json) file.

To let the CARLA Agent execute the scenarios, please run the command stated above but add 'ai' at the end.

Example:
```
bash run.sh [participant's name e.g. carla_agent] ai
```

## Recordings

All simulations are recorded and monitored. The recorded data will be stored in:
`data/recordings/[participant's name]/`

The recording of the simulation itself will be stored in:

  `CarlaUE4/Saved/`
  
```
bash replay.sh [participant's name] [scenario name]
```

This will replay the simulation of scenario driven by the participant.