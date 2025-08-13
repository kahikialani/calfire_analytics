import pandas as pd
import sqlite3

def load_data_from_database():
    print("Loading data from database...")
    conn = sqlite3.connect("calfire_data.db")
    df = pd.read_sql("""
        SELECT * FROM incidents
        WHERE incident_acres_burned IS NOT NULL
        AND incident_acres_burned > 0
        """, conn)
    df['incident_date_created'] = pd.to_datetime(df['incident_date_created'], errors='coerce')
    df['incident_date_extinguished'] = pd.to_datetime(df['incident_date_extinguished'], errors='coerce')
    df['year'] = df['incident_date_created'].dt.year
    df['month'] = df['incident_date_created'].dt.month
    df['month_name'] = df['incident_date_created'].dt.month_name()
    df['day_of_year'] = df['incident_date_created'].dt.dayofyear
    df['duration_days'] = (df['incident_date_extinguished'] - df['incident_date_created'])

    def categorize_fire_size(acres):
        if pd.isna(acres) or acres <= 0:
            return "Unknown"
        elif acres < 10:
            return "Tiny (<10 acres)"
        elif acres < 100:
            return "Small (<100 acres)"
        elif acres < 1000:
            return "Medium (<1,000 acres)"
        elif acres < 10000:
            return "Large (<10,000 acres)"
        elif acres < 100000:
            return "Huge (<100,000 acres)"
        else:
            return "Mega (>100,000 acres)"
    df['fire_size_category'] = df['incident_acres_burned'].apply(categorize_fire_size)
    return df

def basic_statistics(df):
    print("Fire EDA")
    print("---" * 20)
    total_incidents = len(df)
    total_acres = df['incident_acres_burned'].sum()
    avg_fire_size = df['incident_acres_burned'].mean()
    median_fire_size = df['incident_acres_burned'].median()
    largest_fire = df.loc[df['incident_acres_burned'].idxmax()]
    print("Total incidents:", total_incidents)
    print("Total acres:", total_acres)
    print("Average fire size:", avg_fire_size)
    print("Median fire size:", median_fire_size)
    print("Largest fire:", largest_fire)

    min_year = df['year'].min()
    max_year = df['year'].max()
    print(f"Date spans: {min_year} to {max_year}")
    active_count = len(df[df['is_active'] == 'Y'])
    extinguished_count = len(df[df['is_active'] == 'N'])
    print(f"Active count: {active_count}")
    print(f"Extinguished count: {extinguished_count}")

def analyze_by_year(df):
    print("Yearly Trends")
    print("---" * 20)
    yearly_stats = df.groupby('year').agg({
        'incident_name': 'count',
        'incident_acres_burned': ['sum','mean','max']
    }).round(0)
    yearly_stats.columns = ['Incidents', 'Total_Acres', 'Avg_Acres', 'Largest_Fire']
    print(yearly_stats.tail(10))
    print('---' * 20)
    worst_by_count = yearly_stats['Incidents'].idxmax()
    worst_by_acres = yearly_stats['Total_Acres'].idxmax()
    print("Notable Years")
    print(f"Most incidents: {worst_by_count} ({yearly_stats.loc[worst_by_count, 'Incidents']:.0f} fires)")
    print(f"Most acres burned: {worst_by_acres} ({yearly_stats.loc[worst_by_acres, 'Total_Acres']:,.0f} acres)")
    return yearly_stats


def analyze_by_county(df):
    print("\nCounty Trends")
    print("---" * 20)
    # Fix: Use correct column name
    county_stats = df.groupby('incident_county').agg({
        'incident_name': 'count',
        'incident_acres_burned': ['sum', 'mean']
    }).round(0)
    county_stats.columns = ['Incidents', 'Total_Acres', 'Avg_Acres']
    county_stats = county_stats.sort_values('Total_Acres', ascending=False)

    print('Top 10 counties by total acres burned:')
    print(county_stats.head(10))
    print('Top 10 counties by number of incidents:')
    county_by_count = county_stats.sort_values('Incidents', ascending=False)
    print(county_by_count.head(10))
    return county_stats

def analyze_by_month(df):
    print("Monthly Patterns")
    print("---" * 20)
    monthly_stats = df.groupby('month_name').agg({
        'incident_name': 'count',
        'incident_acres_burned': ['sum','mean']
    }).round(0)
    monthly_stats.columns = ['Incidents', 'Total_Acres', 'Avg_Acres']
    month_order = ['January', 'February', 'March', 'April', 'May', 'June','July',
                   'August', 'September', 'October', 'November', 'December']
    monthly_stats = monthly_stats.reindex(month_order)
    peak_count_month = monthly_stats['Incidents'].idxmax()
    peak_acres_month = monthly_stats['Total_Acres'].idxmax()
    print(f"Most incidents: {peak_count_month}")
    print(f"Most acres burned: {peak_acres_month}")
    return monthly_stats

def analyze_fire_sizes(df):
    print("Fire Sizes Analysis")
    print("---" * 20)
    size_distribution = df['fire_size_category'].value_counts()
    print("Fire Sizes Distribution")
    for category, count in size_distribution.items():
        percentage = (count / len(df)) * 100
        print(f" {category}: {percentage:.1f}%")
    mega_fires = df[df['incident_acres_burned'] >= 100000].sort_values('incident_acres_burned', ascending=False)
    if len(mega_fires) > 0:
        print(f"Mega Fires (100,000+ acres): {len(mega_fires)} total")
        for idx, fire in mega_fires.head(10).iterrows():
            print(f"{fire['incident_name']}: {fire['incident_acres_burned']:,.0f} acres ({fire['year']}, {fire['incident_county']})")
    return size_distribution

def create_summary_insights(df):
    total_incidents = len(df)
    total_acres = df['incident_acres_burned'].sum()
    years_span = df['year'].max() - df['year'].min() + 1

    fire_season_months = df[df['month'].isin([6,7,8,9,10])]
    fire_season_pct = (len(fire_season_months)/total_incidents)*100

    large_fires = df[df['incident_acres_burned'] >= 10000]
    large_fires_pct = (len(large_fires) / total_incidents)*100
    large_fires_acres_pct = (large_fires['incident_acres_burned'].sum() / total_incidents)*100
    print("Key Findings:")
    print(f"Analyzed {total_incidents} incidents over {years_span} years")
    print(f"{fire_season_pct:.1f}% of fires occur during June-Oct")
    print(f"Large fires (10,000+ acres) represent {large_fires_pct:.1f}% of incidents but {large_fires_acres_pct:.1f}% of total damage")
    print(f"Average fire size has {'increased' if df.groupby('year')['incident_acres_burned'].mean().iloc[-1] > df.groupby('year')['incident_acres_burned'].mean().iloc[0] else 'decreased'} over time")

    top_county = df.groupby('incident_county')['incident_acres_burned'].sum().idxmax()
    top_county_acres = df.groupby('incident_county')['incident_acres_burned'].sum().max()
    print(f"{top_county} has the most total acres burned ({top_county_acres:.1f} acres)")

def export_analysis_data(df):
    print("Exporting Data")
    import os
    os.makedirs('EDA', exist_ok=True)
    df.to_csv('EDA/incidents_cleaned.csv', index = False)
    print(f"Exported incidents_clead.csv ({len(df)} records)")
    yearly_summary = df.groupby('year').agg({
        'incident_name': 'count',
        'incident_acres_burned': ['sum', 'mean', 'max']
    }).round(2)
    yearly_summary.columns = ['incident_count', 'total_acres', 'avg_acres', 'max_acres']
    yearly_summary.to_csv('EDA/yearly_summary.csv')
    print("exported yearly_summary.csv")

if __name__ == "__main__":
    print("Starting CAL FIRE EDA")
    df = load_data_from_database()
    if len(df) > 0:
        basic_statistics(df)
        yearly_stats = analyze_by_year(df)
        county_stats = analyze_by_county(df)
        monthly_stats = analyze_by_month(df)
        size_stats = analyze_fire_sizes(df)
        create_summary_insights(df)
        export_analysis_data(df)
        print(f"\nFinished EDA of CAL FIRE Incidents Data")
    else:
        print("No Data")







