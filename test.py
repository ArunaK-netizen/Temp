import pandas as pd

# --- Step 1: Read Excel file ---
df = pd.read_excel("lab_allocation.xlsx")   # Replace with your Excel filename

# --- Step 2: Identify the column containing names ---
# Example: if your names are in a column called 'Name'
name_col = "RA Name"  # change to your actual column name

# --- Step 3: Group and count ---
name_counts = df[name_col].value_counts().reset_index()
name_counts.columns = [name_col, "Count"]

# --- Step 4: Save to new Excel file ---
name_counts.to_excel("name_counts.xlsx", index=False)

print("✅ Done! Counts saved to name_counts.xlsx")
