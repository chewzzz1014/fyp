import json
import uuid
from datetime import datetime
import re

def auto_generate_skill_annotations(input_file, output_file):
    """
    Collect SKILL entities from entries with id <= 20919 and auto-annotate entries with id >= 20920.

    Args:
        input_file (str): Path to the input JSON file containing existing annotations.
        output_file (str): Path to save the updated JSON file with auto-generated SKILL annotations.
    """
    print("Starting the skill annotation process...")

    # Load the annotated dataset
    with open(input_file, 'r') as file:
        data = json.load(file)
    print(f"Loaded {len(data)} entries from the input file.")

    # Extract all SKILL keywords from entries with id <= 20919
    skill_keywords = set()
    for entry in data:
        entry_id = entry.get("id", 0)
        if entry_id <= 20919:
            annotations = entry["annotations"][0]["result"]
            for annotation in annotations:
                if "labels" in annotation["value"] and annotation["value"]["labels"][0] == "SKILL":
                    # Strip whitespaces and convert to lowercase
                    skill = annotation["value"]["text"].strip().lower()
                    if skill:  # Ignore empty strings
                        skill_keywords.add(skill)
    print(f"Collected {len(skill_keywords)} unique SKILL keywords.")

    # Process each entry in the dataset
    total_resumes = len(data)
    for idx, entry in enumerate(data, start=1):
        entry_id = entry.get("id", 0)
        if entry_id >= 20920:
            print(f"Processing entry {idx}/{total_resumes} (ID: {entry_id})...")
            text = entry["data"]["Text"]
            annotations = entry["annotations"][0]["result"]
            # Keep track of existing annotated spans (start, end)
            labeled_spans = []

            # Collect existing annotation spans
            for annotation in annotations:
                start = annotation["value"]["start"]
                end = annotation["value"]["end"]
                labeled_spans.append((start, end))

            # Sort spans to ensure no overlap when adding new annotations
            labeled_spans.sort()

            new_annotations = []
            for skill in skill_keywords:
                # Use regex to find whole word matches in the text
                for match in re.finditer(rf"\b{re.escape(skill)}\b", text.lower()):  # Match case-insensitive
                    start_pos, end_pos = match.start(), match.end()

                    # Skip matches that are whitespace only
                    if text[start_pos:end_pos].strip() == "":
                        continue

                    # Check if this span overlaps with any existing annotations
                    is_overlapping = any(
                        start < end_pos and end > start_pos for start, end in labeled_spans
                    )
                    if not is_overlapping:
                        # Add the new annotation
                        new_annotations.append({
                            "value": {
                                "start": start_pos,
                                "end": end_pos,
                                "text": text[start_pos:end_pos],
                                "labels": ["SKILL"]
                            },
                            "id": str(uuid.uuid4()),
                            "from_name": "label",
                            "to_name": "text",
                            "type": "labels",
                            "origin": "manual"
                        })
                        # Add the new span to the list of labeled spans
                        labeled_spans.append((start_pos, end_pos))

            # Sort the spans to maintain proper order
            labeled_spans.sort()
            # Add the new SKILL annotations to the existing ones
            annotations.extend(new_annotations)

            # Update only the annotations field and the modification time
            entry["annotations"][0]["result"] = annotations
            entry["updated_at"] = datetime.now().isoformat()  # Update modification time

            print(f"Added {len(new_annotations)} new annotations to entry ID: {entry_id}.")

    # Save the updated data to a new JSON file
    with open(output_file, 'w') as file:
        json.dump(data, file)
    print(f"Updated annotations saved to {output_file}")


input_file = "removed_skills_1142_resumes_annotated.json"
output_file = "final_1142_resumes_annotated.json"
auto_generate_skill_annotations(input_file, output_file)