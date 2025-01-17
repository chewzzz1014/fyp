# Overview
My Bachelor Degree's Final Year Project with title **AI-Powered Job Application Management for Applicant**. There are 3 main parts in the project
1. Named Entity Recognition (NER)
   - Involved in complete machine-learning lifecycle: dataset annotation, model training, model evaluation
   - Trained 2 NER models using spaCy and Flair library, with manually-annotated resume dataset which can recognise 11 types of entities in resume and job description.
2. Job-Resume Matching Scoring
   - Calculate the matching score between a resume contents and job description in range of 0 (not relevant) to 1 inclusively (very relevant).
   - Perform cosine similarity calculation between resume skills and job description skills which are extracted using NER trained models.
3. ResuMatch, Job Application Management System
   - Develop job application management system consists of Job Management, Resume Management, Job-Resume Matching and Dashboard.
   - Backend: FastAPI and uvicorn
   - Accepts resume in PDF format and job details uploaded by users
   - Perform NER prediction on resume contents (uploaded in PDF format and parsed into text) and job description.
   - Calculate job-resume matching score for each job-resume pair selected by users.
   - Provide a Kanban board for users to update job application status for each job-resume pair between 6 application status:
     - Interested
     - Applied
     - Assessment
     - Interviewing
     - Offer
     - Rejected

## Related Repositories
1. [Frontend code](https://github.com/chewzzz1014/fyp-frontend)
2. [Archive of esume dataset, annotation and trained model](https://github.com/chewzzz1014/fyp-ner-archive)

## NER Entities
| Category            | Entity                      | Label Name  | Example                     |
|---------------------|-----------------------------|-------------|-----------------------------|
| **Personal Information** | Name                        | NAME        | John Doe                    |
|                     | Location                    | LOC         | California                  |
|                     | Phone Number                | PHONE       | 0192394945995               |
|                     | Email Address               | EMAIL       | johndoe@test.com            |
| **Education**       | University or School Name   | UNI         | University of California    |
|                     | Academic Qualification Name | DEG         | Bachelor of Computer Science|
|                     | Study Period                | STUDY PER   | Oct 2021-Jul 2024           |
| **Working Experience** | Job Title                   | JOB         | Java Developer              |
|                     | Company or Organisation Name| COMPANY     | Abc Company                 |
|                     | Working Period              | WORK PER    | Aug 2024-Current            |
| **Skill**           | Skill                       | SKILL       | Java                        |

## Launch Backend Server
1. Activate venv
```
source venv/Scripts/source
```
2. Launch FastiAPI Server
```
uvicorn backend.main:app --reload
```

## Label Studio Setup and Launch
1. Create venv
```
python -m venv venv
```
2. Activate venv
```
source venv/Scripts/activate
```
3. Install Label Studio
```
python -m pip install label-studio
```
4. Launch Label Studio in localhost:8080 (default port)
```
label-studio
```
5. Export annotations
```
label-studio export <project-id> <export-format> --export-path=<output-path>
```