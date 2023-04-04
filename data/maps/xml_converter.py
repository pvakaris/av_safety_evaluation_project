# import functions to read xml file and visualize commonroad objects
import argparse
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.common.file_writer import CommonRoadFileWriter
from commonroad.visualization.mp_renderer import MPRenderer
from commonroad.scenario.scenario import Tag
from commonroad.planning.planning_problem import PlanningProblemSet
from crdesigner.map_conversion.map_conversion_interface import opendrive_to_commonroad

def main():
    
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--fromFile', '-f',
        default='Town04.xodr',
        help='Give the name of the file to convert from')
    argparser.add_argument(
        '--toFile', '-t',
        default='Town4_commonRoad.xml',
        help='Give the name of the file to convert to')
    args = argparser.parse_args()
    
    
    try:
        scenario = opendrive_to_commonroad("./opendrive_format/{}".format(args.fromFile))
        writer = CommonRoadFileWriter(
            scenario=scenario,
            planning_problem_set=PlanningProblemSet(),
            author="Vakaris Paulavicius",
            affiliation="King's College London",
            source="CommonRoad Scenario Designer",
            tags={Tag.URBAN},
        )
        writer.write_to_file("./commonroad_format/{}".format(args.toFile))
    except KeyboardInterrupt:
        pass
    except:
        print("Something wrong happened trying to convert the map.")
    finally:
        print("Finished converting.")
        
if __name__ == '__main__':
    main()
    