"""
Number of AI publications in Gambling by AI topic, 2010–25

Tracks the growth of specific AI sub-fields—such as Machine Learning, NLP, 
and Generative AI—within gambling research, using a multi-line trend 
analysis with color-coded labeling and manual positioning for clarity.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Load the data
df = pd.read_csv('ai_gambling_corpus.csv')

# 2. Filter out "Other" and ensure years are within range
df = df[df['ai_topics'] != 'Other']

# 3. Prepare Pivot Table (Counts)
topic_trend = df.groupby(['publication_year', 'ai_topics']).size().unstack(fill_value=0)

# Ensure the range 2010-2025 is fully represented
all_years = range(2010, 2026)
topic_trend = topic_trend.reindex(all_years, fill_value=0)

# 4. Visual Configuration
colors = {
    "Machine Learning": "#2a5a8e",
    "Computer Vision": "#e1aee1",
    "Pattern Recognition": "#1e606e",
    "Natural Language Processing": "#87ceeb",
    "Knowledge based systems": "#7b2cbf",
    "Generative AI": "#000000",
    "Logic and reasoning": "#da70d6",
    "Multi-agent systems": "#20b2aa",
    "Robots": "#191970"
}

# ADJUST THESE VALUES to nudge labels up (+) or down (-) to prevent overlap
# Example: "Generative AI": 2.5 (nudges it up by 2 units on the Y-axis)
label_offsets = {
    "Machine Learning": 0,
    "Computer Vision": -0.2,
    "Pattern Recognition": -1.7,
    "Natural Language Processing": 0,
    "Knowledge based systems": 2,
    "Generative AI": 0.5,
    "Logic and reasoning": -0.4,
    "Multi-agent systems": 1,
    "Robots": -2
}

# 5. Plotting
plt.figure(figsize=(14, 8), facecolor='white')
ax = plt.gca()

for topic in topic_trend.columns:
    color = colors.get(topic, '#888888')
    
    # Plot the line
    plt.plot(
        topic_trend.index, 
        topic_trend[topic], 
        color=color, 
        linewidth=2.5, 
        marker='o', 
        markersize=3
    )
    
    # Get last valid data point for labeling
    last_year = topic_trend.index[-1]
    last_val = int(topic_trend[topic].iloc[-1])
    
    # Apply the manual offset from the dictionary
    offset = label_offsets.get(topic, 0)

    plt.text(
        last_year + 0.2,            # X-position (just past the last year)
        last_val + offset,         # Y-position (value + manual nudge)
        f"{last_val:,} {topic}",    # Format as integer with thousands separator
        color=color,
        fontweight='bold',
        va='center',
        fontsize=9
    )

# 6. Styling & Cleanup
plt.title('Number of AI publications in Gambling by AI topic, 2010–25', 
          loc='left', fontsize=16, fontweight='bold', pad=30)
plt.ylabel('Number of publications', fontsize=11, labelpad=10)
plt.xlabel('Year', fontsize=11)

# Remove chart junk
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='-', alpha=0.1)

# Set axis limits and ticks
plt.xlim(2010, 2029)  # Extra room on the right for long labels
plt.xticks(all_years)

# 7. Export and Show
plt.tight_layout()
plt.savefig('ai_topic_count_trends.png', dpi=300, bbox_inches='tight')
plt.show()