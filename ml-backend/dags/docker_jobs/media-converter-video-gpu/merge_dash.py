"""
Merge a base dash mpd file with an additional dash mpd file
"""

import argparse
import xml.etree.ElementTree as ET


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input-base-file", default="uuid.wav.word.json", type=str, help="Input file base dash mpd"
    )
    parser.add_argument(
        "-a", "--input-additional-file", default="uuid.wav.word.json", type=str, help="Input file additional dash mpd"
    )
    parser.add_argument("-o", "--output-file", default="uuid.json", type=str, help="Output dash mpd file")
    return parser.parse_args()


def main():
    """
    Convert a whisper word level ASR result our ASR result structure
    """
    args = parse_args()
    ET.register_namespace("", "urn:mpeg:dash:schema:mpd:2011")

    # Load base dash mpd
    main_tree = ET.parse(args.input_base_file)
    root = main_tree.getroot()
    last_rep_id = 0

    # Get last representation id of main dash mpd
    for adaptation_set in root.iter("{urn:mpeg:dash:schema:mpd:2011}AdaptationSet"):
        curr_rep_id = int(adaptation_set.findall("{urn:mpeg:dash:schema:mpd:2011}Representation")[-1].get("id"))
        if curr_rep_id > last_rep_id:
            last_rep_id = curr_rep_id
    print(f"Highest base representation id: {last_rep_id}")

    # Load additional dash mpd
    add_tree = ET.parse(args.input_additional_file)
    add_root = add_tree.getroot()
    # Get all additional representations
    add_reps = []
    for adaptation_set in add_root.iter("{urn:mpeg:dash:schema:mpd:2011}AdaptationSet"):
        curr_reps = adaptation_set.findall("{urn:mpeg:dash:schema:mpd:2011}Representation")
        add_reps = add_reps + curr_reps

    count = 1
    for adaptation_set in root.iter("{urn:mpeg:dash:schema:mpd:2011}AdaptationSet"):
        # AdaptationSet 0 is video
        # AdaptationSet 1 is audio
        id = adaptation_set.get("id")
        print(f"AdaptationSet: {id}")
        if id == "0":
            # ET.dump(adaptation_set)
            print("adding additonal video Representations")
            for rep in add_reps:
                if rep.get("mimeType") == "video/mp4":
                    rep.set("id", str(last_rep_id + count))
                    print("Adding Representation")
                    # ET.dump(rep)
                    count += 1
                    adaptation_set.append(rep)
            print(f"Modified video AdaptationSet: {id}")
            # ET.dump(adaptation_set)
        elif id == "1":
            # ET.dump(adaptation_set)
            print("adding additonal audio Representations")
            for rep in add_reps:
                if rep.get("mimeType") == "audio/mp4":
                    rep.set("id", str(last_rep_id + count))
                    print("Adding Representation")
                    # ET.dump(rep)
                    count += 1
                    adaptation_set.append(rep)
            print(f"Modified audio AdaptationSet: {id}")
            # ET.dump(adaptation_set)

    main_tree.write(args.output_file, "utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
