import json
from collections import defaultdict
import uuid  # To generate unique IDs for auto-generated annotations
from datetime import datetime  # To update modification time
import re  # For word boundary matching


def auto_generate_skill_annotations(input_file, output_file):
    """
    Auto-generate SKILL annotations for whole words without overlapping annotations.
    
    Args:
        input_file (str): Path to the input JSON file containing existing annotations.
        output_file (str): Path to save the updated JSON file with auto-generated SKILL annotations.
    """
    # Load the annotated dataset
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Extract all existing SKILL labels from the annotations
    skill_keywords = set()
    for entry in data:
        annotations = entry["annotations"][0]["result"]
        for annotation in annotations:
            if "labels" in annotation["value"] and annotation["value"]["labels"][0] == "SKILL":
                skill = annotation["value"]["text"].strip().lower()  # Strip whitespaces and convert to lowercase
                if skill:  # Ignore empty strings
                    skill_keywords.add(skill)

    print(f"Extracted SKILL keywords: {skill_keywords}")  # Debugging: View extracted skills

    # Process each entry in the dataset
    total_resumes = len(data)  # Total number of resumes
    for idx, entry in enumerate(data, start=1):  # Add a counter for progress tracking
        text = entry["data"]["Text"]
        annotations = entry["annotations"][0]["result"]
        labeled_spans = []  # Keep track of existing annotated spans (start, end)

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
                            "text": text[start_pos:end_pos],  # Preserve original casing
                            "labels": ["SKILL"]
                        },
                        "id": str(uuid.uuid4()),  # Generate a unique ID
                        "from_name": "label",
                        "to_name": "text",
                        "type": "labels",
                        "origin": "manual"  # Use 'manual' to avoid Label Studio import issues
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
        
        # Print progress
        print(f"Processing resume {idx}/{total_resumes}...")

    # Save the updated data to a new JSON file
    with open(output_file, 'w') as file:
        json.dump(data, file)
    print(f"Updated annotations saved to {output_file}")


# Example usage
input_file = "1142_resumes_annotated.json"  # Replace with your input file
output_file = "updated_1142_resumes_annotated.json"  # Replace with your desired output file
auto_generate_skill_annotations(input_file, output_file)