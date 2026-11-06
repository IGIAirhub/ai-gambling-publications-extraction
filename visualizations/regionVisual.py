"""
AI publications in Gambling (% of total) by region, 2010–25

Citations of AI publications in Gambling (% of total) by region, 2010–25

Maps institutional affiliations to global geographic regions and visualizes 
the annual relative share of both publication volume and citation impact 
using normalized trend lines and region-specific labeling.

From the World Bank Region Grouping
https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups

Note: Regions can receive multiple counts per paper if multiple countries in the same region are
represented but each country is represented only once per paper.

"""

import pandas as pd
import matplotlib.pyplot as plt
import ast

east_asia_pacific = {
    'AS', 'AU', 'BN', 'KH', 'CN', 'FJ', 'PF', 'GU', 'HK', 'ID', 
    'JP', 'KI', 'KP', 'KR', 'LA', 'MO', 'MY', 'MH', 'FM', 'MN', 
    'MM', 'NR', 'NC', 'NZ', 'MP', 'PW', 'PG', 'PH', 'WS', 'SG', 
    'SB', 'TW', 'TH', 'TL', 'TO', 'TV', 'VU', 'VN'
}

europe_central_asia = {
    'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'JE', 'GG', 
    'HR', 'CY', 'CZ', 'DK', 'EE', 'FO', 'FI', 'FR', 'GE', 'DE', 'GI', 
    'GR', 'GL', 'HU', 'IS', 'IE', 'IM', 'IT', 'KZ', 'XK', 'KG', 'LV', 
    'LI', 'LT', 'LU', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 'PL', 'PT', 
    'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TJ', 'TR', 
    'TM', 'UA', 'GB', 'UZ'
}

latin_america_caribbean = {
    'AG', 'AR', 'AW', 'BS', 'BB', 'BZ', 'BO', 'BR', 'VG', 'KY', 
    'CL', 'CO', 'CR', 'CU', 'CW', 'DM', 'DO', 'EC', 'SV', 'GD', 
    'GT', 'GY', 'HT', 'HN', 'JM', 'MX', 'NI', 'PA', 'PY', 'PE', 
    'PR', 'SX', 'KN', 'LC', 'MF', 'VC', 'SR', 'TT', 'TC', 'UY', 
    'VE', 'VI'
}

middle_east_north_africa = {
    'AF', 'DZ', 'BH', 'DJ', 'EG', 'IR', 'PK', 'MT', 'IQ', 'IL', 'JO', 'KW',
    'LB', 'LY', 'MA', 'OM', 'QA', 'SA', 'SY', 'TN', 'AE', 'PS', 'YE'
}

north_america = {
    'BM', 'CA', 'US'
}

south_asia = {
    'BD', 'BT', 'IN', 'MV', 'NP', 'LK'
}

sub_saharan_africa = {
    'AO', 'BJ', 'BW', 'BF', 'BI', 'CV', 'CM', 'CF', 'TD', 'KM',
    'CD', 'CG', 'CI', 'GQ', 'ER', 'SZ', 'ET', 'GA', 'GM', 'GH',
    'GN', 'GW', 'KE', 'LS', 'LR', 'MG', 'MW', 'ML', 'MR', 'MU',
    'MZ', 'NA', 'NE', 'NG', 'RW', 'ST', 'SN', 'SC', 'SL', 'SO',
    'ZA', 'SS', 'SD', 'TZ', 'TG', 'UG', 'ZM', 'ZW'
}

def parse_affiliations(x):
    if x == "[]" or x == []:
        return []
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except:
        return None  # parse failed

def map_region(country_code):
    code = str(country_code).upper().strip()
    if code in east_asia_pacific: return 'East Asia and Pacific'
    if code in europe_central_asia: return 'Europe and Central Asia'
    if code in latin_america_caribbean: return 'Latin America and the Caribbean'
    if code in north_america: return 'North America'
    if code in south_asia: return 'South Asia'
    if code in sub_saharan_africa: return 'Sub-Saharan Africa'
    if code in middle_east_north_africa: return 'Middle East and North Africa'
    return 'Other'

# 3. Processing the logic: One count per institution -> Country -> Region
def get_paper_regions(affiliations):
    # If no affiliations, mark as Unknown
    if not affiliations or len(affiliations) == 0:
        return ['Unknown']

    # 1) Deduplicate by country
    unique_countries = set()

    for aff in affiliations:
        country = aff.get('country')
        if country and str(country).strip():
            unique_countries.add(str(country).upper().strip())

    if not unique_countries:
        return ['Unknown']

    # 2) Map each unique country to a region
    #    IMPORTANT: do NOT dedupe regions here, because NA=2 if US+CA.
    paper_regions = [map_region(cc) for cc in unique_countries]

    return paper_regions if paper_regions else ['Unknown']


# 1. Load the data
df = pd.read_csv('ai_gambling_corpus.csv')
df['affiliations'] = df['affiliations'].apply(parse_affiliations)
df['regions_list'] = df['affiliations'].apply(get_paper_regions)
df['cited_by_count'] = pd.to_numeric(df['cited_by_count'], errors='coerce').fillna(0)

# Create a readable string version of the regions for the CSV
df['regions_allocated'] = df['regions_list'].apply(lambda x: ', '.join(x))

# Choose which columns to save (dropping the heavy abstract column)
export_cols = [col for col in df.columns if col != 'title_abstract_combined']
df[export_cols].to_csv('ai_gambling_with_regions.csv', index=False)
print("Saved regional data to 'ai_gambling_with_regions.csv'")
# ==========================================

# 2. Continue with your plotting logic
# Explode the list so each region count becomes a row for the VISUALIZATION
df_exploded = df.explode('regions_list').dropna(subset=['regions_list'])

# Explode the list so each region count becomes a row
df_exploded = df.explode('regions_list').dropna(subset=['regions_list'])

# 4. Prepare Pivot Table
pub_trend = df_exploded.groupby(['publication_year', 'regions_list']).size().unstack(fill_value=0)
cit_trend = df_exploded.groupby(['publication_year', 'regions_list'])['cited_by_count'].sum().unstack(fill_value=0)

# Filter for the years 2010-2025
pub_trend = pub_trend.loc[2010:2025]
cit_trend = cit_trend.loc[2010:2025]

# 5. Plotting (AI Index Style)
colors = {
    'North America': '#1a73b8',
    'Europe and Central Asia': '#e587d1',
    'East Asia and Pacific': '#006d6d',
    'South Asia': '#79d2f2',
    'Middle East and North Africa': '#8c4b8c',
    'Latin America and the Caribbean': '#99e6e6',
    'Sub-Saharan Africa': '#f4a582'
}

pub_label_offsets = {
    'South Asia': 0.5,
    'Latin America and the Caribbean': 0.2,
    'Middle East and North Africa': -1.0,
    'Sub-Saharan Africa': -0.7
}

cit_label_offsets = {
    'North America': 0.8,
    'East Asia and Pacific': -0.5,
    'Unknown': -0.5,
    'South Asia': -2.3,
    'Latin America and the Caribbean': 0.5,
    'Middle East and North Africa': -1.0,
    'Sub-Saharan Africa': 0.3
}

pub_trend = pub_trend.div(pub_trend.sum(axis=1), axis=0) * 100
cit_trend = cit_trend.div(cit_trend.sum(axis=1), axis=0) * 100


plt.figure(figsize=(12, 8), facecolor='white')
ax = plt.gca()

for region in pub_trend.columns:
    color = colors.get(region, '#888888')
    plt.plot(pub_trend.index, pub_trend[region], color=color, linewidth=2.5, marker='o', markersize=2)
    
    # Label at the end: Percentage of the entire corpus for that year
    last_year = pub_trend.index[-1]
    last_val = pub_trend[region].iloc[-1]

    offset = pub_label_offsets.get(region, 0)

    plt.text(
        last_year + 0.2,
        last_val + offset,
        f"{last_val:.1f}% {region}",
        color=color,
        fontweight='bold',
        va='center',
        fontsize=9
    )

# Styling
plt.title('AI publications in Gambling (% of total) by region, 2010–25', 
          loc='left', fontsize=15, fontweight='bold', pad=30)
plt.ylabel('AI publications in Gambling (% of total)', fontsize=10, labelpad=10)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='-', alpha=0.1)
plt.xlim(2010, 2028) # Extra space for labels
plt.xticks(range(2010, 2026, 1))

plt.tight_layout()
plt.savefig('regional_trends.png', dpi=300)
plt.show()


# Citations Plot
plt.figure(figsize=(12, 8), facecolor='white')
ax = plt.gca()

for region in cit_trend.columns:
    color = colors.get(region, '#888888')
    plt.plot(
        cit_trend.index,
        cit_trend[region],
        color=color,
        linewidth=2.5,
        marker='o',
        markersize=2
    )

    # Label at the end: % of total citations for that year
    last_year = cit_trend.index[-1]
    last_val = cit_trend[region].iloc[-1]

    offset = cit_label_offsets.get(region, 0)

    plt.text(
        last_year + 0.2,
        last_val + offset,
        f"{last_val:.1f}% {region}",
        color=color,
        fontweight='bold',
        va='center',
        fontsize=9
    )

# Styling
plt.title(
    'Citations of AI publications in Gambling (% of total) by region, 2010–25',
    loc='left',
    fontsize=15,
    fontweight='bold',
    pad=30
)
plt.ylabel('Citations (% of total that year)', fontsize=10, labelpad=10)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='-', alpha=0.1)
plt.xlim(2010, 2028)  # Extra space for labels
plt.xticks(range(2010, 2026, 1))

plt.tight_layout()
plt.savefig('regional_citation_trends.png', dpi=300)
plt.show()