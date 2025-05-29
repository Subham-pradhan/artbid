import os
import sys
import django
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error


# --- Django Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artbid_project.settings')
django.setup()

# --- Now it's safe to import Django modules ---
from auctions.models import AuctionData
from auctions.utils import calculate_artist_reputation

def train_price_predictor():
    print("Starting training...")

    # Recalculate artist reputation
    calculate_artist_reputation()

    data = AuctionData.objects.all()
    records = [{
        'artist_reputation': a.artist_reputation,
        'style': a.style,
        'starting_price': a.starting_price,
        'final_price': a.final_price,
    } for a in data if a.final_price is not None]

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("No auction data available for training.")

    # Encode style
    le = LabelEncoder()
    df['style_encoded'] = le.fit_transform(df['style'])

    # Feature matrix and target
    X = df[['artist_reputation', 'style_encoded', 'starting_price']]
    y = df['final_price']

    print(df)
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)

    # Save model and encoder
    os.makedirs('auctions/ml/models', exist_ok=True)
    joblib.dump(model, 'auctions/ml/models/price_model.pkl')
    joblib.dump(le, 'auctions/ml/models/style_encoder.pkl')

    # Evaluate model
    preds = model.predict(X)
    mae = mean_absolute_error(y, preds)
    mse = mean_squared_error(y, preds)

    print(f"Training completed. MAE: {mae:.2f}, MSE: {mse:.2f}")
    return mae, mse
    
    

if __name__ == "__main__":
    try:
        mae, mse = train_price_predictor()
    except Exception as e:
        print(f"Error: {e}")
