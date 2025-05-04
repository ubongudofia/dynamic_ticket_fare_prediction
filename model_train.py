import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('fare_prediction/synthetic_fare_data.csv')

# Basic features
basic_features = ['distance_km', 'departure_hour', 'is_peak_hour', 'seat_availability_ratio']

# Enhanced features with interactions
df['distance_peak_interaction'] = df['distance_km'] * df['is_peak_hour']
df['distance_demand_interaction'] = df['distance_km'] * (1 - df['seat_availability_ratio'])
enhanced_features = basic_features + ['distance_peak_interaction', 'distance_demand_interaction']

# Business-rule inspired features
df['base_distance'] = df['distance_km'] * 100  # Assuming base rate of 100 per km
df['peak_adjustment'] = df['is_peak_hour'] * 0.2  # 20% peak surcharge
df['demand_adjustment'] = (1 - df['seat_availability_ratio']) * 0.3  # 30% max demand surcharge
business_rule_features = ['base_distance', 'peak_adjustment', 'demand_adjustment']

# Target variable
target = 'final_fare'

# Function to evaluate models
def evaluate_model(X, y, model, name):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n{name} Model Performance:")
    print(f"RMSE: {rmse:.2f}")
    print(f"R-squared: {r2:.4f}")
    
    # Plot feature importance if available
    if hasattr(model, 'coef_'):
        if len(model.coef_) <= 10:  # Only plot for reasonable number of features
            plt.figure(figsize=(10, 5))
            if isinstance(X, pd.DataFrame):
                features = X.columns
            else:
                features = [f"Feature {i}" for i in range(X.shape[1])]
            plt.barh(features, model.coef_)
            plt.title(f'{name} Model Coefficients')
            plt.xlabel('Coefficient Value')
            plt.tight_layout()
            plt.show()
    
    return rmse, r2

# Approach 1: Basic Linear Regression
print("\n=== Approach 1: Basic Linear Regression ===")
basic_model = LinearRegression()
evaluate_model(df[basic_features], df[target], basic_model, "Basic Linear Regression")

# Approach 2: Enhanced Features
print("\n=== Approach 2: Enhanced Features ===")
enhanced_model = LinearRegression()
evaluate_model(df[enhanced_features], df[target], enhanced_model, "Enhanced Features")

# Approach 3: Business Rule Features
print("\n=== Approach 3: Business Rule Features ===")
business_model = LinearRegression()
evaluate_model(df[business_rule_features], df[target], business_model, "Business Rule Features")

# Approach 4: Polynomial Regression
print("\n=== Approach 4: Polynomial Regression (Degree=2) ===")
poly_model = make_pipeline(
    PolynomialFeatures(degree=2, include_bias=False),
    LinearRegression()
)
evaluate_model(df[enhanced_features], df[target], poly_model, "Polynomial Regression")

# Approach 5: Combined Best Features
print("\n=== Approach 5: Combined Best Features ===")
combined_features = enhanced_features + business_rule_features
combined_model = LinearRegression()
evaluate_model(df[combined_features], df[target], combined_model, "Combined Features")

# Print summary of all approaches
print("\n=== Model Comparison Summary ===")
print("Model\t\t\tRMSE\t\tR-squared")
print("------------------------------------------------")
approaches = {
    "Basic Linear": (basic_features, basic_model),
    "Enhanced Features": (enhanced_features, enhanced_model),
    "Business Rules": (business_rule_features, business_model),
    "Polynomial (deg=2)": (enhanced_features, poly_model),
    "Combined Features": (combined_features, combined_model)
}

for name, (features, model) in approaches.items():
    X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=42)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print(f"{name.ljust(20)}{rmse:.2f}\t\t{r2:.4f}")





# === Approach 1: Basic Linear Regression ===

# Basic Linear Regression Model Performance:
# RMSE: 255.73
# R-squared: 0.9321

# === Approach 2: Enhanced Features ===

# Enhanced Features Model Performance:
# RMSE: 233.70
# R-squared: 0.9433

# === Approach 3: Business Rule Features ===

# Business Rule Features Model Performance:
# RMSE: 255.74
# R-squared: 0.9321

# === Approach 4: Polynomial Regression (Degree=2) ===

# Polynomial Regression Model Performance:
# RMSE: 227.60
# R-squared: 0.9462

# === Approach 5: Combined Best Features ===

# Combined Features Model Performance:
# RMSE: 233.70
# R-squared: 0.9433

# === Model Comparison Summary ===
# Model                   RMSE            R-squared
# ------------------------------------------------
# Basic Linear        255.73              0.9321
# Enhanced Features   233.70              0.9433
# Business Rules      255.74              0.9321
# Polynomial (deg=2)  227.60              0.9462
# Combined Features   233.70              0.9433