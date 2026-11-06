import pandas as pd
import matplotlib.pyplot as plt
import ast
import numpy as np

# 1. Load and Parse Data
df = pd.read_csv('filtered_openalex_works.csv')

def parse_affiliations(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except:
        return []

df['affiliations'] = df['affiliations'].apply(parse_affiliations)

# 2. Filter for Years and Identify Top 100 Most Cited
target_years = [2023, 2024, 2025]
df_recent = df[df['publication_year'].isin(target_years)].copy()

# Select the top 100 most cited papers across this 3-year window
top_100_papers = df_recent.nlargest(100, 'cited_by_count')

# 3. Explode Affiliations to Organizations
# We extract the name of every organization affiliated with these top papers
org_data = []
for _, row in top_100_papers.iterrows():
    year = row['publication_year']
    # Use a set to ensure an org is only counted once per paper
    seen_orgs_in_paper = set() 
    for aff in row['affiliations']:
        org_name = aff.get('name')
        if org_name and org_name not in seen_orgs_in_paper:
            org_data.append({'year': year, 'org': org_name})
            seen_orgs_in_paper.add(org_name)

df_orgs = pd.DataFrame(org_data)

# 4. Count and Pivot
# Get counts per Org and Year
counts = df_orgs.groupby(['org', 'year']).size().unstack(fill_value=0)

# Identify the top 10 organizations overall for the chart
counts['total'] = counts.sum(axis=1)
top_orgs = counts.sort_values('total', ascending=False).head(10).drop(columns='total')

# 5. Plotting (AI Index Style)
colors = {
    2023: '#006d6d', # Dark Teal
    2024: '#e587d1', # Pink/Purple
    2025: '#1a73b8'  # Blue
}

fig, ax = plt.subplots(figsize=(14, 8), facecolor='white')

x = np.arange(len(top_orgs.index))
width = 0.25  # Width of each bar
multiplier = 0

for year in target_years:
    if year in top_orgs.columns:
        offset = width * multiplier
        rects = ax.bar(x + offset, top_orgs[year], width, label=str(year), color=colors[year])
        
        # Add value labels on top of bars
        ax.bar_label(rects, padding=3, fontsize=9, fontweight='bold', color='#444444')
        multiplier += 1

# Final Visual Styling
plt.title('Number of highly cited publications in top 100 by organization, 2023–25', 
          loc='left', fontsize=14, fontweight='bold', pad=30)

ax.set_xticks(x + width, top_orgs.index)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.ylabel('Number of publications', fontsize=10)

# Remove clutter
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
plt.grid(axis='y', linestyle='-', alpha=0.2)

# Legend at the top
ax.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=3, frameon=False)

plt.tight_layout()
plt.savefig('cited_by_organization.png', dpi=300)
plt.show()