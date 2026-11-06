"""
Sports betting publications by sport (% of total), 2010–25

Visualizes the relative share of research for specific athletic categories—
such as Football, Horse Racing, and Cricket—within the sports betting 
corpus, featuring normalized annual percentages and cumulative volume labels.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Load the data
df = pd.read_csv('ai_gambling_corpus.csv')

# 2. Define the core sports topics
SPORTS_TOPICS = [
    "Basketball", "American Football", "Football/Soccer", 
    "Horse Racing", "Cricket", "Tennis", "Baseball", 
    "Combat Sport", "Ice Hockey", "Multi-sport"
]

# AI Index-style color palette
colors = {
    "Basketball": "#1a73b8",
    "American Football": "#e587d1",
    "Football/Soccer": "#006d6d",
    "Horse Racing": "#79d2f2",
    "Cricket": "#8c4b8c",
    "Tennis": "#f4a582",
    "Baseball": "#2a5a8e",
    "Combat Sport": "#e1aee1",
    "Ice Hockey": "#1e606e",
    "Multi-sport": "#7b2cbf"
}

label_offsets = {
    "Basketball": 0.0,
    "American Football": -.6,
    "Football/Soccer": 0.0,
    "Horse Racing": -2.6,
    "Cricket": 0.0,
    "Tennis": 0.0,
    "Baseball": 2.6,
    "Combat Sport": 0.0,
    "Ice Hockey": 1.3,
    "Multi-sport": -1.3
}

# ==========================================
# TOGGLE "OTHER" CATEGORY
# ==========================================
SPORTS_TOPICS.append("Other")
colors["Other"] = "#999999"       
label_offsets["Other"] = 0.7     
# ==========================================

# 3. Filter for years and specific topics
df = df[df['sport_topic'].isin(SPORTS_TOPICS)]
df = df[(df['publication_year'] >= 2010) & (df['publication_year'] <= 2025)]

# 4. Prepare Pivot Table (Counts first)
topic_trend = df.groupby(['publication_year', 'sport_topic']).size().unstack(fill_value=0)

# Ensure all years and all topics are represented
all_years = range(2010, 2026)
topic_trend = topic_trend.reindex(index=all_years, columns=SPORTS_TOPICS, fill_value=0)

# 5. CONVERT TO PERCENTAGE
# Divide each row by the sum of that row (total publications that year)
topic_trend_pct = topic_trend.div(topic_trend.sum(axis=1), axis=0) * 100
topic_trend_pct = topic_trend_pct.fillna(0) # Handle years with zero total papers

# Calculate total raw counts for the parenthesis label
raw_totals = topic_trend.sum()

# 6. Plotting
plt.figure(figsize=(15, 8), facecolor='white')
ax = plt.gca()

for topic in SPORTS_TOPICS:
    color = colors.get(topic, '#888888')
    
    # Plot the percentage line
    plt.plot(
        topic_trend_pct.index, 
        topic_trend_pct[topic], 
        color=color, 
        linewidth=2.5, 
        marker='o', 
        markersize=3
    )
    
    # Get last percentage value and the historical raw total
    last_year = topic_trend_pct.index[-1]
    last_val_pct = topic_trend_pct[topic].iloc[-1]
    total_raw = int(raw_totals[topic])
    
    offset = label_offsets.get(topic, 0)

    # Label: "XX.X% Topic Name (Total RawCount)"
    plt.text(
        last_year + 0.2,            
        last_val_pct + offset,         
        f"{last_val_pct:.1f}% {topic} (Total {total_raw:,})",    
        color=color,
        fontweight='bold',
        va='center',
        fontsize=9
    )

# 7. Styling
plt.title('Sports betting publications by sport (% of total), 2010–25', 
          loc='left', fontsize=16, fontweight='bold', pad=30)
plt.ylabel('Percentage of annual publications', fontsize=11, labelpad=10)
plt.xlabel('Year', fontsize=11)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='-', alpha=0.1)

# --- THE KEY CHANGE ---
# Setting the lower limit to a small negative number (e.g., -2) 
# creates that extra breathing room below the 0 line.
current_max = topic_trend_pct.max().max()
plt.ylim(-4, current_max * 1.15) 
# ---------------------

plt.xlim(2010, 2026) # Adjusted slightly wider for the longer "Total" labels
plt.xticks(all_years)

plt.tight_layout()
plt.savefig('sports_betting_percentage_trends.png', dpi=300, bbox_inches='tight')
plt.show()