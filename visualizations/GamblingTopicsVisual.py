"""
Number of AI publications by gambling topic, 2010–25

Categorizes research by specific gambling domains—such as Sports Betting, 
Poker, and Problem Gambling—to visualize longitudinal volume trends and 
identify the fastest-growing application areas for AI.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Load the data
df = pd.read_csv('ai_gambling_corpus.csv')

# 2. Define the topics (excluding "Other" for the plot)
TOPICS = [
    "Sports Betting", 
    "Poker", 
    "Online Problem Gambling", 
    "Casino Surveillance", 
    "Gambling Decision Making", 
    "Gambling Website Detection"
]

colors = {
    "Sports Betting": "#1a73b8",
    "Poker": "#e587d1",
    "Online Problem Gambling": "#006d6d",
    "Casino Surveillance": "#79d2f2",
    "Gambling Decision Making": "#8c4b8c",
    "Gambling Website Detection": "#f4a582"
}

# ADJUST THESE VALUES to nudge labels up (+) or down (-) 
# Use this to separate labels that are too close together in 2025
label_offsets = {
    "Sports Betting": 0.0,
    "Poker": 0.0,
    "Online Problem Gambling": 0.0,
    "Casino Surveillance": 0.0,
    "Gambling Decision Making": 0.0,
    "Gambling Website Detection": 0.0
}


# ==========================================
# TOGGLE "OTHER" CATEGORY
# Un-comment the three lines below to include "Other" in the visual
# ==========================================
TOPICS.append("Other")
colors["Other"] = "#999999"       # Neutral Grey
label_offsets["Other"] = 0.0     # Adjust if it overlaps
# ==========================================

# 3. Filter for years and specific topics
df = df[df['gambling_topic'].isin(TOPICS)]
df = df[(df['publication_year'] >= 2010) & (df['publication_year'] <= 2025)]

# 4. Prepare Pivot Table (Counts)
topic_trend = df.groupby(['publication_year', 'gambling_topic']).size().unstack(fill_value=0)

# Ensure all years and all topics are represented (even if zero)
all_years = range(2010, 2026)
topic_trend = topic_trend.reindex(index=all_years, columns=TOPICS, fill_value=0)

# ==========================================
# TOGGLE "OTHER" CATEGORY
# Un-comment the three lines below to include "Other" in the visual
# ==========================================
# TOPICS.append("Other")
# colors["Other"] = "#999999"       # Neutral Grey
# label_offsets["Other"] = 0.0     # Adjust if it overlaps
# ==========================================

# 6. Plotting
plt.figure(figsize=(14, 8), facecolor='white')
ax = plt.gca()

for topic in TOPICS:
    color = colors.get(topic, '#888888')
    
    # Plot the line
    plt.plot(
        topic_trend.index, 
        topic_trend[topic], 
        color=color, 
        linewidth=2.5, 
        marker='o', 
        markersize=3,
        label=topic
    )
    
    # Get last valid data point for labeling
    last_year = topic_trend.index[-1]
    last_val = int(topic_trend[topic].iloc[-1])
    
    # Apply the manual offset from the dictionary
    offset = label_offsets.get(topic, 0)

    # Label text: "Count Topic Name"
    plt.text(
        last_year + 0.2,            # Position slightly to the right of the last point
        last_val + offset,         # Y-position with manual nudge
        f"{last_val:,} {topic}",    
        color=color,
        fontweight='bold',
        va='center',
        fontsize=10
    )

# 7. Styling & Cleanup
plt.title('Number of AI publications by gambling topic, 2010–25', 
          loc='left', fontsize=16, fontweight='bold', pad=30)
plt.ylabel('Number of publications', fontsize=11, labelpad=10)
plt.xlabel('Year', fontsize=11)

# Remove chart junk
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='-', alpha=0.1)

# Set axis limits and ticks
plt.xlim(2010, 2031)  # Extra room for labels
plt.xticks(all_years)

# 8. Export
plt.tight_layout()
plt.savefig('gambling_topic_trends_final.png', dpi=300, bbox_inches='tight')
plt.show() # Uncomment if running locally