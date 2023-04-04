import xml.etree.ElementTree as ET
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import sys

def draw_bar_chart(args):
    # Parse XML file
    try:
        tree = ET.parse(args.xml_file)
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        sys.exit(1)
    root = tree.getroot()
    names = []
    scores = []
    for participant in root:
        name = participant.find("Name").text
        try:
            score = float(participant.find("Analysis").find(args.category).text)
        except ValueError as e:
            print(f"Error parsing score value: {e}")
            sys.exit(1)
        names.append(name)
        scores.append(score)
    
    # Plot bar chart
    sns.set_palette("Blues", color_codes=True)
    sns.set_style("darkgrid")
    sns.set(font_scale=1.3)

    sns.set_context("notebook")
    sns.barplot(x=names, y=scores)
    plt.xlabel(args.xlabel)
    plt.ylabel("Penalty Points")
    plt.title(args.title)
    if args.save:
        try:
            plt.savefig(args.save)
        except Exception as e:
            print(f"Error saving the diagram: {e}")
            sys.exit(1)
    plt.show()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml_file", type=str, help="Path to the XML file")
    parser.add_argument("--category", type=str, help="Category of the data")
    parser.add_argument("--save", type=str, help="Path to save the diagram")
    parser.add_argument("--title", type=str, help="Title of the diagram")
    parser.add_argument("--xlabel", type=str, help="xlabel text")
    args = parser.parse_args()

    # Draw bar chart
    draw_bar_chart(args)

if __name__ == "__main__":
    main()
