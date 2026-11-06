"""
Number of AI publications in Gambling by venue type, 2010–25

Consolidates and filters publication data by venue type—such as Journals, 
Conferences, and Repositories—to visualize longitudinal growth trends 
using professional end-of-line labeling and an AI Index-inspired palette.
"""

import pandas as pd
import matplotlib.pyplot as plt

# 1. Load and Prepare Data
df = pd.read_csv('ai_gambling_corpus.csv')

# Consolidate book series and ebook platform to just "book"
df['venue_type'] = df['venue_type'].replace({
    'book series': 'book', 
    'ebook platform': 'book'
})

# Do not include unknown types in the visualization
filtered_df = df[df['venue_type'] != 'unknown']

# Create a "Pivot Table": Rows = Year, Columns = Venue Type, Values = Count
# unstack(fill_value=0) ensures years with 0 publications don't break the line
trend_data = filtered_df.groupby(['publication_year', 'venue_type']).size().unstack(fill_value=0)
# 2. Setup the "AI Index" Color Palette (Estimated from your image)
colors = {
    'journal': '#1a73b8',      # Strong Blue
    'conference': '#e587d1',   # Pink/Lavender
    'repository': '#006d6d',   # Dark Teal
    'book': '#79d2f2',         # Sky Blue
    'other': '#8c4b8c',        # Purple
    'dissertation': '#99e6e6'  # Pale Cyan
}

# 3. Plotting
plt.figure(figsize=(12, 7), facecolor='white')
ax = plt.gca()

for column in trend_data.columns:
    # Get color from our map, default to gray if venue isn't in map
    line_color = colors.get(column.lower(), '#888888')
    
    # Plot the line
    line = plt.plot(trend_data.index, trend_data[column], 
                    color=line_color, linewidth=2.5, marker=None)
    
    # 4. End-of-Line Labeling (The "Professional" Touch)
    # This places text at the very last data point of each line
    last_year = trend_data.index[-1]
    last_value = trend_data[column].iloc[-1]

    y_pos = last_value  # Default position
    
    if column.capitalize() == 'Repository':
        y_pos += 1  # Move Repository UP by 1 unit
    elif column.capitalize() == 'Conference':
        y_pos -= 2  # Move Conference DOWN by 2 units
    
    plt.text(last_year + 0.2, y_pos, f"{last_value}, {column.capitalize()}", 
             color=line_color, fontweight='bold', va='center', fontsize=10)

# 5. Visual Styling to match the AI Index
plt.title('Number of AI publications in Gambling by venue type, 2010–25', 
          loc='left', fontsize=16, fontweight='bold', pad=30)
plt.ylabel('Number of AI publications in Gambling', fontsize=11, labelpad=10)

# Clean up axes: Remove top and right borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add very light horizontal grid lines
plt.grid(axis='y', linestyle='-', alpha=0.15)

# Adjust X-axis to make room for labels on the right
plt.xlim(trend_data.index.min(), trend_data.index.max() + 3)
plt.xticks(trend_data.index) # Show every year on the axis

plt.tight_layout()
plt.savefig('venue_trends_comparison.png', dpi=300)
