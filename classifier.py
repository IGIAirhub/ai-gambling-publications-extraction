import cso_classifier as CSOClassifier
from cso_classifier import CSOClassifier
import json

with open("gambling_publications.json", "r", encoding="utf-8") as f:
    publications = json.load(f)

cc = CSOClassifier(
    modules = "both",                       # It will catch syntactic and semantic concepts
    explanation = False,                    # This tells WHY it was labeled, disable for high volume runs
    delete_outliers = False,                # Self explanatory, deletes outliers and oddball topics
    fast_classification= True,              # Less accurate, but faster
    enhancement = "first",
    workers = 6,
    filter_by = [                           # Hone down on AI and ML topics
        "artificial intelligence",
        "machine learning",
    ]
)

result = cc.batch_run(publications)

output = {}
for key in publications.keys():
    output[key] = result[key].get('union', [])

with open('classifier_results.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)