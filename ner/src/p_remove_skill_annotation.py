import json
from datetime import datetime

def auto_generate_skill_annotations(input_file, output_file):
    """
    Remove specified skills for entries with IDs >= 20920.

    Args:
        input_file (str): Path to the input JSON file containing existing annotations.
        output_file (str): Path to save the updated JSON file with modified annotations.
    """
    # Skills to exclude
    skills_to_exclude = {
        "design", "designing", "development", "testing", "architecture", "server", "analysis", "editing", "coding",
        "responsible", "database", "monitoring", "managing", "deployment", "motivated", "selfmotivated", "planning",
        "installation", "repair", "troubleshoot", "troubleshooting", "building", "analytical", "maintenance",
        "design development", "installing", "training", "supporting", "system", "deployment", "writing",
        "adminstration", "access", "sql", "office", "power", "server", "integration", "analysis", "bi", "assessment"
    }

    # Load the annotated dataset
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Process each entry in the dataset
    total_resumes = len(data)
    for idx, entry in enumerate(data, start=1):
        entry_id = entry.get("id", 0)
        # if entry_id >= 20920:
        if entry_id >= 0:
            annotations = entry["annotations"][0]["result"]

            # Remove annotations for skills in the exclusion list
            annotations = [
                annotation for annotation in annotations
                if annotation["value"]["text"].strip().lower() not in skills_to_exclude
            ]

            # Update only the annotations field and the modification time
            entry["annotations"][0]["result"] = annotations
            entry["updated_at"] = datetime.now().isoformat()  # Update modification time

        # Print progress
        print(f"Processing resume {idx}/{total_resumes}...")

    # Save the updated data to a new JSON file
    with open(output_file, 'w') as file:
        json.dump(data, file)
    print(f"Updated annotations saved to {output_file}")


input_file = "1142_resumes_annotated.json"
output_file = "removed_skills_1142_resumes_annotated.json"
auto_generate_skill_annotations(input_file, output_file)