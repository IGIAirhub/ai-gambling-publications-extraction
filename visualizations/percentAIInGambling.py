"""
AI Publications in Gambling Research (%), 2010–25

Calculates the annual percentage of AI-related publications within the 
broader gambling research corpus and visualizes the trend using 
Stanford AI Index-inspired line styling.

Requires two CSV files:
1. ai_gambling_corpus.csv - The existing dataset of AI+Gambling publications.
2. just_gambling_publications.csv - A new dataset containing all gambling-related publications (including those without AI focus) for the same years.
"""
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. LOAD LOCAL DATA ---
# CSV 1: Your existing AI+Gambling file
# Columns: openalex_id, publication_year, etc.
df_ai = pd.read_csv('ai_gambling_corpus.csv') 

# CSV 2: The gambling metadata we just created
# Columns: openalex_id, publication_year
df_total = pd.read_csv('just_gambling_publications.csv')

# --- 2. AGGREGATE BY YEAR ---
years = range(2010, 2026)
stats = []

for yr in years:
    # Count AI+G papers in this year
    a_count = len(df_ai[df_ai['publication_year'] == yr])
    
    # Count Total Gambling papers in this year
    g_count = len(df_total[df_total['publication_year'] == yr])
    
    # Calculate % (AI share of the total gambling corpus)
    percentage = (a_count / g_count * 100) if g_count > 0 else 0
    
    stats.append({"Year": yr, "AI_Share": percentage})

df_plot = pd.DataFrame(stats)

# --- 3. STANFORD AI INDEX STYLING ---
zfig, ax = plt.subplots(figsize=(10, 6), dpi=100)

# Branding Colors
NAVY = "#002D72"  # Stanford Navy
SOFT_GRID = "#EEEEEE"

# Plot the trend
ax.plot(df_plot['Year'], df_plot['AI_Share'], 
        color=NAVY, linewidth=3, 
        marker='o', markersize=8, mfc='white', mew=2, label="AI Share")

# Aesthetics
ax.set_facecolor('white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, color=SOFT_GRID)
ax.set_axisbelow(True)

# Labels
ax.set_title("AI Publications in Gambling Research (%)", 
             fontsize=16, fontweight='bold', loc='left', pad=20)
ax.set_ylabel("Percent of Total Gambling Research", fontsize=11, labelpad=10)
ax.set_xlabel("Year", fontsize=11)

# Annotate the most recent year
final_val = df_plot['AI_Share'].iloc[-1]
ax.annotate(f"{final_val:.1f}%", 
            xy=(2025, final_val), xytext=(5, 5), 
            textcoords='offset points', fontweight='bold', color=NAVY)

plt.tight_layout()
plt.savefig("gambling_ai_trends_final.png")
plt.show()