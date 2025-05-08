import os
import pandas as pd 
import numpy as np 
# from datetime import datetime

# Configuration
np.random.seed(42)
hours = pd.date_range(start="2024-04-07", end="2024-04-13", freq = "H")
regions = ['East', 'Central', 'West']
user_ids = [f'user_{i}' for i in range(1, 101)]

def generate_base(n):
    return {
        'timestamp': hours[:n],
        'region': np.random.choice(regions, n),
        'user_id': np.random.choice(user_ids, n),
        'age': np.random.randint(18, 65, n),
        'gender': np.random.choice(['M', 'F', 'Other'], n),
        'income_level': np.random.choice(['Low', 'Medium', 'High'], n),
    }
    

def save_csv(filename, data):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    
def generate_online(channel):
    n = len(hours)
    data = generate_base(n)
    data.update({
        'channel_type': 'Online',
        'channel_name': channel,
        'channel_id': f"{channel.lower().replace(' ', '_')}_01",
        'ad_cost': np.random.uniform(5, 500, n),
        'sales': np.random.uniform(10, 1000, n),
        'homepage_visits': np.random.randint(100, 10000, n),
        'branded_searches': np.random.randint(10, 1000, n),
        'conversion_rate': np.random.uniform(0.01, 0.15, n),
        'bounce_rate': np.random.uniform(0.2, 0.9, n),
        'top_searched_words': np.random.choice(['product_x', 'promo_y', 'brand_z'], n),
        'search_volume': np.random.randint(1000, 10000, n),
        'share_of_voice': np.random.uniform(0.01, 0.5, n),
        'brand_awareness': np.random.uniform(0.2, 0.9, n),
        'recall_score': np.random.uniform(0.1, 1.0, n),
        'social_sentiment': np.random.uniform(-1, 1, n),
        'engagement': np.random.randint(0, 500, n)
    })
    
    filepath = os.path.join("data", f"{channel.lower().replace(' ', '_')}_data.csv")
    save_csv(filepath, data)
    

def generate_offline(channel):
    n = len(hours)
    data = generate_base(n)
    data.update({
        'channel_type': 'Offline',
        'channel_name': channel,
        'channel_id': f"{channel.lower().replace(' ', '_')}_01",
        'ad_cost': np.random.uniform(50, 1000, n),
        'sales': np.random.uniform(50, 2000, n),
        'impressions': np.random.randint(1000, 100000, n),
        'reach': np.random.randint(500, 50000, n),
        'grps': np.random.uniform(5, 100, n),
        'brand_awareness': np.random.uniform(0.2, 0.9, n),
        'recall_score': np.random.uniform(0.1, 1.0, n)
    })
    filepath = os.path.join("data", f"{channel.lower().replace(' ', '_')}_data.csv")
    save_csv(filepath, data)


def generate_crm():
    n = 500
    data = {
        'timestamp': np.random.choice(hours, n),
        'user_id': np.random.choice(user_ids, n),
        'region': np.random.choice(regions, n),
        'purchase_value': np.random.uniform(50, 1000, n),
        'products_viewed': np.random.randint(1, 10, n),
        'membership_status': np.random.choice(['Basic', 'Premium'], n)
    }
    filepath = os.path.join("data", "crm_data.csv")
    save_csv(filepath, data)


def generate_brand_survey():
    n = 200
    data = {
        'timestamp': np.random.choice(hours, n),
        'user_id': np.random.choice(user_ids, n),
        'region': np.random.choice(regions, n),
        'brand_awareness': np.random.uniform(0.2, 0.9, n),
        'recall_score': np.random.uniform(0.1, 1.0, n),
        'survey_type': np.random.choice(['Awareness', 'Consideration', 'Preference'], n)
    }
    filepath = os.path.join("data", "brand_awareness_survey.csv")
    save_csv(filepath, data)


def generate_sales():
    n = 300
    data = {
        'timestamp': np.random.choice(hours, n),
        'user_id': np.random.choice(user_ids, n),
        'region': np.random.choice(regions, n),
        'sales_value': np.random.uniform(10, 1000, n),
        'product_category': np.random.choice(['A', 'B', 'C'], n),
        'channel': np.random.choice(
            ["Google Ads", "Meta Ads", "TV", "Radio", "Billboard"], n
        )
    }
    filepath = os.path.join("data", "sales_data.csv")
    save_csv("sales_data.csv", data)


def generate_all_samples():
    """
    """
    for ch in ["Google Ads", "Google Analytics", "Meta Ads", "Instagram", "Twitter", "TikTok"]:
        generate_online(ch)
    
    for ch in ["TV", "Radio", "Billboard"]:
        generate_offline(ch)
    
    generate_crm()
    
    generate_brand_survey()
    
    generate_sales()


# Define a mock data generator
def generate_mock_data(source_name, channel_type, size=len(hours)):
    return pd.DataFrame({
        'timestamp': hours,
        'channel_type': channel_type,
        'channel_name': source_name,
        'channel_id': f'{source_name}_001',
        'ad_cost': np.random.uniform(50, 500, size),
        'sales': np.random.uniform(1000, 10000, size),
        'homepage_visits': np.random.randint(100, 1000, size),
        'branded_searches': np.random.randint(50, 300, size),
        'conversion_rate': np.random.uniform(0.01, 0.20, size),
        'bounce_rate': np.random.uniform(0.20, 0.80, size),
        'top_searched_words': np.random.choice(
            ['sofa', 'dining table', 'wardrobe', 'IKEA', 'JYSK', 'KIKA'], size),
        'search_volume': np.random.randint(100, 10000, size),
        'share_of_voice': np.random.uniform(0.01, 0.40, size),
        'region': np.random.choice(['North', 'South', 'East', 'West'], size),
        'user_id': np.random.randint(10000, 99999, size),
        'age': np.random.randint(18, 70, size),
        'gender': np.random.choice(['Male', 'Female', 'Other'], size),
        'income_level': np.random.choice(['Low', 'Medium', 'High'], size),
        'brand_awareness': np.random.uniform(0.1, 1.0, size),
        'recall_score': np.random.uniform(0.1, 1.0, size),
        'social_sentiment': np.random.uniform(-1.0, 1.0, size),
        'engagement': np.random.randint(10, 500, size)
    })
    

def merge_the_samples(online_sources, offline_sources, customer_sources):
    """_summary_
    """
    # Generate and combine
    online_df = pd.concat([generate_mock_data(src, 'online') for src in online_sources], ignore_index=True)
    offline_df = pd.concat([generate_mock_data(src, 'offline') for src in offline_sources], ignore_index=True)
    customer_df = pd.concat([generate_mock_data(src, 'customer') for src in customer_sources], ignore_index=True)
    
    # Combine all into one DataFrame
    combined_df = pd.concat([online_df, offline_df, customer_df], ignore_index=True)
    
    # Save to CSV
    filepath = os.path.join("data", 'mock_combined_marketing_data.csv')
    combined_df.to_csv(filepath, index=False)