from itertools import chain
import pyalex
from pyalex import Works
import json

pyalex.config.email = ""

search_terms = [
    # === RESPONSIBLE GAMING ===
    # Core responsibility and harm reduction terms
    "responsible gambling",
    "responsible gaming",
    "safer gambling",
    "gambling harm",
    "gambling prevention",
        
    # === ONLINE GAMBLING ===
    # Digital and internet-based gambling platforms
    "online gambling",
    "internet gambling",
    "online casino",
    "online betting",
    "mobile gambling",
    "mobile betting",
    "remote gambling",
    "remote betting",
    "digital gambling",
    "online wagering",
    "virtual casino",
    "online poker",
    "online slots",
    
    # Mobile and app-based gambling
    "gambling apps",
    "gambling websites",
    "online bookmaker",
    "betting apps",
    "casino apps",
    
    # === SPORTS BETTING ===
    # General sports wagering terms
    "sports betting",
    "sports wagering",
    "online sportsbook",
    
    # Sport-specific betting
    "football betting",
    "basketball betting",
    "baseball betting",
    "horse racing",
    "race betting",
    "NBA betting",
    "NHL betting",
    "NFL betting",
    "MLB betting",
    "MLS betting",
    
    # Emerging betting types
    "esports betting",
    
    # === PROBLEM GAMBLING ===
    # Clinical and diagnostic terms
    "problem gambling",
    "pathological gambling",
    "gambling disorder",
    "gambling addiction",
    "compulsive gambling",
    "disordered gambling",
    "gambling problems",
    "at-risk gambling",
    
    # Assessment and treatment
    "gambling severity",
    "gambling treatment",
    "gambling therapy",
    "gambling recovery",
    "gambling counseling",
    "gambling screening",
    "PGSI score",        # Problem Gambling Severity Index
    "gambling relapse",
    
    # === LAND-BASED CASINO ===
    # Physical casino venues
    "land-based casino",
    "casino gambling",
    "casino gaming",
    "brick-and-mortar casino",
    "tribal casino",
    
    # Electronic gaming machines (EGMs)
    "slot machines",
    "slot gambling",
    "electronic gaming machines",
    "EGM gambling",      # Electronic Gaming Machines
    "video lottery terminals",
    "poker machines",
    
    # Table games
    "casino poker",
    "blackjack gambling",
    "roulette gambling",
    "craps gambling",
    "baccarat gambling",
    
    # === REGULATORY & ECONOMIC ===
    # Policy and regulation
    "gambling regulation",
    "gambling regulator",
    "gambling policy",
    "gambling legislation",
    "gambling commission",
    
    # Economic aspects
    "gambling revenue",
    "gambling tax",
    "gambling industry",
    "gambling operators",
    "gambling expenditure",
    
    # Population studies
    "gambling prevalence",
    "gambling participation",
    
    # === BEHAVIORAL RESEARCH ===
    # Behavioral patterns and psychology
    "gambling behavior",
    "gambling patterns",
    "gambling frequency",
    "gambling motivation",
    "gambling attitudes",
    "gambling beliefs",
    "gambling cognitions",
    "gambling risk",

    # === GENERAL ===
    # Broad terms for our search
    "ai in gambling",
    "gambling sector",
    "gambling industry",
    "gambling-related",
    "case of gambling"
]

def reconstruct_abstract(inv_idx):
    if not inv_idx:
        return None
    max_pos = max(pos for positions in inv_idx.values() for pos in positions)
    words = [None] * (max_pos + 1)
    for word, positions in inv_idx.items():
        for pos in positions:
            words[pos] = word
    return " ".join([w for w in words if w])

# Query: all gambling-related works since 2022
pager = (
    Works()
    .filter(**{
                "title_and_abstract.search": ' OR '.join([f'"{term}"' for term in search_terms]),
                "from_publication_date": "2010-01-01",
                "type": "article|review",
                "language": "en"
              }
           )
    .paginate(per_page=200, n_max=None)
)

# Dictionary of publications
publications = {}

for work in chain.from_iterable(pager):
    work_id = work.get("id", "unknown_id")
    title = work.get("display_name", "No Title")
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    keywords_list = [c["display_name"] for c in work.get("concepts", [])]
    keywords = ", ".join(keywords_list) if keywords_list else "No Keywords"

    publications[work_id] = {
        "title": title,
        "abstract": abstract,
        # "abstract": "",
        # "keywords": keywords
        "keywords": ""
    }

with open('gambling_publications.json', 'w', encoding='utf-8') as f:
    json.dump(publications, f, indent=2, ensure_ascii=False)
