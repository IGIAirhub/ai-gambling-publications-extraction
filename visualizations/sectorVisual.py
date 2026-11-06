"""
AI publications in Gambling (% of total) by Primary Sector, 2010–25

Analyzes the organizational landscape of research by identifying the primary 
sector (Academia, Industry, Government, etc.) of each publication and 
visualizing their relative annual shares as a percentage of the total corpus.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import ast

# 1. Load Data
df = pd.read_csv('ai_gambling_corpus.csv')

def parse_affiliations(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except:
        return []

df['affiliations'] = df['affiliations'].apply(parse_affiliations)

# 2. Sector Mapping
def map_sector(raw_type):
    t = str(raw_type).lower().strip()
    mapping = {
        'education': 'Academia',
        'company': 'Industry',
        'government': 'Government',
        'nonprofit': 'Nonprofit'
    }
    return mapping.get(t, 'Other')

# 3. NEW LOGIC: Primary Sector (First Institution Only)
def get_primary_sector(affiliations):
    # If empty, exclude from the list (paper is ignored in final count)
    if not affiliations or len(affiliations) == 0:
        return None 
    
    # Grab the VERY FIRST institution in the list
    first_aff = affiliations[0]
    sector_type = first_aff.get('sector', 'unknown')
    
    return map_sector(sector_type)

df['primary_sector'] = df['affiliations'].apply(get_primary_sector)

# 4. Aggregate (1:1 Relationship)
# Drop papers with no sector data
df_filtered = df.dropna(subset=['primary_sector'])

# Simple count of papers per year per primary sector
sector_counts = df_filtered.groupby(['publication_year', 'primary_sector']).size().unstack(fill_value=0)

# Filter for the target years (2013-2023)
years = range(2010, 2026)
sector_counts = sector_counts.loc[sector_counts.index.intersection(years)]

# Calculate percentage share per year 
# (Now each paper counts exactly once toward the 100% total)
sector_pct = sector_counts.div(sector_counts.sum(axis=1), axis=0) * 100

# 5. Plotting (AI Index Style)
colors = {
    'Academia': '#1a73b8',   
    'Industry': '#006d6d',   
    'Government': '#79d2f2', 
    'Nonprofit': '#e587d1',  
    'Other': '#4a148c'       
}

label_offsets = {
    'Industry': -1.0,
    'Government': -2.3,
    'Nonprofit': 1.3
}

plt.figure(figsize=(12, 7), facecolor='white')
ax = plt.gca()

category_order = ['Academia', 'Industry', 'Government', 'Nonprofit', 'Other']

for sector in category_order:
    if sector in sector_pct.columns:
        color = colors.get(sector, '#888888')
        plt.plot(sector_pct.index, sector_pct[sector], color=color, linewidth=2.5)
        
        # Label at the end of the line
        last_year = sector_pct.index[-1]
        last_val = sector_pct[sector].iloc[-1]

        offset = label_offsets.get(sector, 0)

        plt.text(last_year + 0.1, last_val + offset, f"{last_val:.2f}%, {sector}", 
                 color=color, fontweight='bold', va='center', fontsize=9)

# Visual Styling
plt.title('AI publications in Gambling (% of total) by Primary Sector, 2010–25', 
          loc='left', fontsize=14, fontweight='bold', pad=25)
plt.ylabel('Share of Total Publications (%)', fontsize=10)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='-', alpha=0.1)
plt.xlim(2010, 2026) 
plt.ylim(-4, 105)
plt.xticks(range(2010, 2026))

ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100, decimals=0))

plt.tight_layout()
plt.savefig('sector_trends.png', dpi=300)
plt.show()