import pandas as pd
import plotly.graph_objects as go

# --- STEP 1: LOAD THE DATA ---
try:
    df = pd.read_csv('user_data.csv')
    print("✅ Data Loaded Successfully!")
except FileNotFoundError:
    print("❌ Error: 'user_data.csv' not found.")
    exit()

# --- STEP 2: DEFINE THE FUNNEL ORDER ---
funnel_steps = ['landing_page', 'product_page', 'add_to_cart', 'checkout_page', 'purchase_success']
df['stage'] = pd.Categorical(df['stage'], categories=funnel_steps, ordered=True)


# --- STEP 3: GROUP DATA TO GET COUNTS ---
funnel_df = df.groupby('stage',observed=True)['user_id'].nunique().reset_index()
funnel_df.columns = ['stage', 'unique_users']

# --- STEP 4: CALCULATE METRICS ---
funnel_df['previous_stage_users'] = funnel_df['unique_users'].shift(1)

# Conversion Rate
funnel_df['step_conversion_rate'] = round((funnel_df['unique_users'] / funnel_df['previous_stage_users']) * 100, 2)

# Drop-off Rate
funnel_df['drop_off_rate'] = 100 - funnel_df['step_conversion_rate']

# Overall Conversion Rate
total_start_users = funnel_df.loc[0, 'unique_users']
funnel_df['overall_conversion_rate'] = round((funnel_df['unique_users'] / total_start_users) * 100, 2)

# --- 🛠️ FIX IS HERE (SIRF NUMERIC COLUMNS KO FILL KARENGE) ---
cols_to_fill = ['previous_stage_users', 'step_conversion_rate', 'drop_off_rate', 'overall_conversion_rate']
funnel_df[cols_to_fill] = funnel_df[cols_to_fill].fillna(0)

print("\n--- 📊 FINAL FUNNEL ANALYSIS REPORT ---")
print(funnel_df[['stage', 'unique_users', 'step_conversion_rate', 'drop_off_rate', 'overall_conversion_rate']])

# --- STEP 5: VISUALIZATION ---
fig = go.Figure(go.Funnel(
    y = funnel_df['stage'],
    x = funnel_df['unique_users'],
    textinfo = "value+percent initial",
    marker = {"color": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]}
))

fig.update_layout(title_text='User Journey Funnel Analysis')
fig.show()

# --- STEP 6: FINDING THE BOTTLENECK ---
# We skip the first row (Landing Page) because drop_off is 0 there
worst_stage = funnel_df.iloc[1:].loc[funnel_df.iloc[1:]['drop_off_rate'].idxmax()]

print("\n--- 🚨 BOTTLENECK DETECTED ---")
print(f"The biggest drop-off is at: {worst_stage['stage']}")
print(f"We lost {worst_stage['drop_off_rate']}% of users here.")