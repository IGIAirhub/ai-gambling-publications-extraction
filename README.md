# About
This repository contains a data-pipeline designed to identify academic publications on Artificial Intelligence and Gambling by leveraging the OpenAlex API and the CSO Classifier. After identification, relevant information is extracted utilizing the OpenAlex API.

## Getting Started
### Set-up
 1. Clone the repository
 2. Download Python 3.8.19 and create a virtual environment (PyEnv)
 3. Install requirements ```pip install -r requirements.txt```
5. One time setup for CSO Classifier ```python setupClassifier.py```

Now the data-pipeline is ready to be executed

## Usage
### Step 1: Query Gambling Publications ``python extract_gambling_publications.py``
- (Optional but recommended) Add your email in the ``pyalex.config.email`` field. This improves performance and provides OpenAlex with data.
- The query extracts the title, abstract, and keywords of gambling publications which is flatten then written to a dictionary with the OpenAlex link as the key and the title, abstract, and keywords as the value.
- **Output:** ``gambling_publications.json``

### Step 2: Classify Gambling Publications ``python classifier.py``
- This script loads ``gambling_publications.json`` and runs a batch classification of every publication in the JSON file, labeling them with topics.
- The ``union`` of the syntactic and semantic labels are written to a dictionary with the OpenAlex link as the key and the label topics as the value
- **Output:** ``classifier_results.json``

### Step 3: Filter for AI/ML Publications  ``python filter_gambling_publications.py``
- This script loads ``classifier_results.json`` and filters the classifier results
- The OpenAlex IDs of publications labeled AI/ML are stored in a list ``filtered_ids.json``
- Utilizing the OpenAlex IDs, the relevant publication's id, doi, title, publication year, institutions, and cited by count are extracted and stored in a dictionary
- **Output:** ``filtered_ids.json``, ``filtered_works.json``

## Methodology
This pipeline uses a three-step data pipeline to identify research that sits at the intersection of Gambling and Artificial Intelligence.
### 1. Gather Publications on Gambling
First, I queried the **OpenAlex API** to retrieve a broad set of gambling-related publications.
-   **Search Strategy:** Single word "gambling" often returns irrelevant results (e.g., "gambling on a business decision") As a result, word pairs were utilized for the query. These included terms like "problem gambling," "online casino," and "sports betting" to ensure the papers were about the gambling sector.
-   **Filters:** Query was restricted to "articles" and "reviews" published from 2010 to present day keeps the dataset relevant  

### 2. AI and ML Classification
Using the **CSO (Computer Science Ontology) Classifier**, the gambling publications are classified on computer science topics.

-   **Classification:** The classifier analyzes the titles and abstracts of the gambling dataset to identify specific research topics. Both the syntactic and semantic modules are searched to catch direct word matches and broader conceptual links.
-   **Targeting AI:** The classifier specifically looks for papers labeled with "artificial intelligence" or "machine learning" to see which of the gambling papers involved computational methods.

### 3. Filter
Results are filtered to create the final dataset of publications that are cross disciplinary between gambling and AI/ML.

-   **Selection:** Classifier results are cross referenced to only keep papers that contain both gambling keywords (from step 1) and AI/ML labels (from step 2).
-   **Final Data Retrieval:** Using the IDs of these specific papers, OpenAlex is queried a second time to extract detailed metadata for analysis, including the DOI, author institutions, country of origin, and citation counts.