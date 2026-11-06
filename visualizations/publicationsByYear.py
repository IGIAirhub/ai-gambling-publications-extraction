"""
Number of AI publications in Gambling worldwide, 2010–25

Loads AI-related gambling publication data and generates a professionally 
styled bar chart of annual publication counts (2010–2025).
"""
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
df = pd.read_csv('ai_gambling_corpus.csv')

# 2. Aggregation
year_counts = df['publication_year'].value_counts().sort_index()

# 3. Create the Styled Bar Chart
fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

# Use the specific "AI Index Blue" (#1a73b8) and remove edges
bars = ax.bar(year_counts.index.astype(str), year_counts.values, 
              color='#1a73b8', width=0.6)

# 4. Add the bold value label to the LAST bar only
last_bar = bars[-1]
ax.text(last_bar.get_x() + last_bar.get_width()/2, last_bar.get_height() + 1,
        f'{int(last_bar.get_height())}', ha='center', va='bottom', 
        fontsize=10, fontweight='bold', color='#1a73b8')

# 5. Professional Titles and Source Info
plt.title('Number of AI publications in Gambling worldwide, 2010–25', 
          loc='left', fontsize=14, fontweight='bold', pad=25)

# Adding the small sub-header for source (matching the visual)
ax.text(0, 1.04, 'Source: OpenAlex | Chart: 2025 Research Report', 
        transform=ax.transAxes, fontsize=9, color='#555555')

plt.ylabel('Number of publications', fontsize=10, labelpad=10)

# 6. Clean up the axes (The "Open" Look)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

# Set grid to be very light and behind the bars
ax.yaxis.grid(True, linestyle='-', alpha=0.15)
ax.set_axisbelow(True)

# Formatting ticks
plt.xticks(rotation=0, fontsize=10) # Keep years horizontal
plt.yticks(fontsize=10)

# 7. Save and Show
plt.tight_layout()
plt.savefig('styled_publications_bar.png', dpi=300)
plt.show()