"""
Monthly Electricity Bill Prediction System
Predicts electricity bills using historical consumption and usage patterns
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

def generate_electricity_data(n_samples=1200, random_state=42):
    """Generate synthetic electricity consumption and bill data"""
    np.random.seed(random_state)
    
    data = []
    
    for i in range(n_samples):
        # Month (1-12)
        month = np.random.randint(1, 13)
        
        # Base consumption varies by season
        if month in [6, 7, 8]:  # Summer - higher AC usage
            base_consumption = np.random.uniform(400, 600)
        elif month in [12, 1, 2]:  # Winter - higher heating
            base_consumption = np.random.uniform(350, 550)
        else:  # Mild seasons
            base_consumption = np.random.uniform(250, 400)
        
        # Household characteristics
        household_size = np.random.randint(1, 8)
        house_area_sqft = np.random.randint(800, 4000)
        age_of_appliances = np.random.randint(1, 20)
        
        # Appliance usage (hours per day)
        ac_usage_hours = np.random.uniform(0, 12)
        heating_usage_hours = np.random.uniform(0, 10)
        water_heater_hours = np.random.uniform(1, 8)
        refrigerator_hours = 24  # Always on
        lighting_hours = np.random.uniform(4, 12)
        
        # Calculate total consumption (kWh)
        ac_consumption = ac_usage_hours * 3.5 * (1 + 0.05 * age_of_appliances / 10)
        heating_consumption = heating_usage_hours * 4.0 * (1 + 0.05 * age_of_appliances / 10)
        water_heater_consumption = water_heater_hours * 4.5
        refrigerator_consumption = refrigerator_hours * 0.8
        lighting_consumption = lighting_hours * 0.15 * (house_area_sqft / 1000)
        other_consumption = np.random.uniform(20, 80)
        
        total_consumption = (ac_consumption + heating_consumption + water_heater_consumption + 
                           refrigerator_consumption + lighting_consumption + other_consumption)
        
        # Occupancy rate (percentage of time someone is home)
        occupancy_rate = np.random.uniform(30, 100)
        
        # Adjust consumption based on occupancy
        adjusted_consumption = total_consumption * (occupancy_rate / 100)
        
        # Tariff rate ($/kWh) - varies by region and season
        base_tariff = np.random.uniform(0.10, 0.18)
        if month in [6, 7, 8, 12, 1, 2]:  # Peak season surcharge
            tariff_rate = base_tariff * 1.15
        else:
            tariff_rate = base_tariff
        
        # Fixed charges
        fixed_charge = np.random.uniform(10, 30)
        
        # Calculate bill
        variable_charge = adjusted_consumption * tariff_rate
        total_bill = fixed_charge + variable_charge
        
        # Add some noise
        noise = np.random.normal(0, total_bill * 0.05)
        total_bill = max(fixed_charge, total_bill + noise)
        
        data.append({
            'Record_ID': f'REC{i+1:05d}',
            'Month': month,
            'Household_Size': household_size,
            'House_Area_SqFt': house_area_sqft,
            'Age_Of_Appliances': age_of_appliances,
            'AC_Usage_Hours': ac_usage_hours,
            'Heating_Usage_Hours': heating_usage_hours,
            'Water_Heater_Hours': water_heater_hours,
            'Lighting_Hours': lighting_hours,
            'Occupancy_Rate': occupancy_rate,
            'Total_Consumption_kWh': adjusted_consumption,
            'Tariff_Rate': tariff_rate,
            'Fixed_Charge': fixed_charge,
            'Monthly_Bill': total_bill
        })
    
    return pd.DataFrame(data)

def prepare_features(df):
    """Prepare features for modeling"""
    df_copy = df.copy()
    
    feature_cols = ['Month', 'Household_Size', 'House_Area_SqFt', 'Age_Of_Appliances',
                   'AC_Usage_Hours', 'Heating_Usage_Hours', 'Water_Heater_Hours',
                   'Lighting_Hours', 'Occupancy_Rate', 'Total_Consumption_kWh', 'Tariff_Rate']
    
    X = df_copy[feature_cols]
    y = df_copy['Monthly_Bill']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    return X_scaled, y, scaler

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple regression models"""
    models = {}
    results = []
    
    # Linear Regression
    print("Training Linear Regression...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    
    models['Linear Regression'] = lr
    results.append({
        'Model': 'Linear Regression',
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_lr)),
        'MAE': mean_absolute_error(y_test, y_pred_lr),
        'R2_Score': r2_score(y_test, y_pred_lr),
        'MAPE': np.mean(np.abs((y_test - y_pred_lr) / y_test)) * 100
    })
    
    # Random Forest
    print("Training Random Forest...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    models['Random Forest'] = rf
    results.append({
        'Model': 'Random Forest',
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
        'MAE': mean_absolute_error(y_test, y_pred_rf),
        'R2_Score': r2_score(y_test, y_pred_rf),
        'MAPE': np.mean(np.abs((y_test - y_pred_rf) / y_test)) * 100
    })
    
    # Gradient Boosting
    print("Training Gradient Boosting...")
    gb = GradientBoostingRegressor(n_estimators=100, random_state=42)
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    
    models['Gradient Boosting'] = gb
    results.append({
        'Model': 'Gradient Boosting',
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
        'MAE': mean_absolute_error(y_test, y_pred_gb),
        'R2_Score': r2_score(y_test, y_pred_gb),
        'MAPE': np.mean(np.abs((y_test - y_pred_gb) / y_test)) * 100
    })
    
    return models, pd.DataFrame(results), y_test, y_pred_lr, y_pred_rf, y_pred_gb

def plot_consumption_distribution(df):
    """Plot electricity consumption distribution and characteristics"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Monthly consumption pattern
    monthly_consumption = df.groupby('Month')['Total_Consumption_kWh'].mean()
    axes[0, 0].plot(monthly_consumption.index, monthly_consumption.values, marker='o', linewidth=2.5, 
                   markersize=8, color='#3498db')
    axes[0, 0].fill_between(monthly_consumption.index, monthly_consumption.values, alpha=0.3, color='#3498db')
    axes[0, 0].set_xlabel('Month', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Average Consumption (kWh)', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Monthly Electricity Consumption Pattern', fontsize=12, fontweight='bold')
    axes[0, 0].grid(alpha=0.3)
    axes[0, 0].set_xticks(range(1, 13))
    
    # Household size vs consumption
    household_consumption = df.groupby('Household_Size')['Total_Consumption_kWh'].mean()
    axes[0, 1].bar(household_consumption.index, household_consumption.values, color='#2ecc71', 
                   alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0, 1].set_xlabel('Household Size', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Average Consumption (kWh)', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Electricity Consumption by Household Size', fontsize=12, fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Bill distribution
    axes[1, 0].hist(df['Monthly_Bill'], bins=30, color='#e74c3c', alpha=0.7, edgecolor='black')
    axes[1, 0].axvline(df['Monthly_Bill'].mean(), color='#2c3e50', linestyle='--', linewidth=2.5, label=f'Mean: ${df["Monthly_Bill"].mean():.2f}')
    axes[1, 0].set_xlabel('Monthly Bill ($)', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Distribution of Monthly Electricity Bills', fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)
    
    # Occupancy rate vs bill
    axes[1, 1].scatter(df['Occupancy_Rate'], df['Monthly_Bill'], alpha=0.6, s=50, 
                      color='#f39c12', edgecolor='black', linewidth=0.5)
    z = np.polyfit(df['Occupancy_Rate'], df['Monthly_Bill'], 1)
    p = np.poly1d(z)
    axes[1, 1].plot(df['Occupancy_Rate'].sort_values(), p(df['Occupancy_Rate'].sort_values()), 
                   "r--", linewidth=2, label='Trend')
    axes[1, 1].set_xlabel('Occupancy Rate (%)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Monthly Bill ($)', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Occupancy Rate vs Monthly Bill', fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/electricity_consumption_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: electricity_consumption_distribution.png")
    plt.close()

def plot_model_comparison(results_df):
    """Plot model performance comparison"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    metrics = ['RMSE', 'MAE', 'R2_Score', 'MAPE']
    
    for idx, metric in enumerate(metrics):
        row = idx // 2
        col = idx % 2
        
        axes[row, col].bar(results_df['Model'], results_df[metric], color=colors, alpha=0.8, 
                          edgecolor='black', linewidth=1.5)
        axes[row, col].set_ylabel(metric, fontsize=11, fontweight='bold')
        axes[row, col].set_title(f'{metric} Comparison', fontsize=12, fontweight='bold')
        axes[row, col].grid(axis='y', alpha=0.3)
        axes[row, col].tick_params(axis='x', rotation=45)
        
        for i, v in enumerate(results_df[metric]):
            axes[row, col].text(i, v + (results_df[metric].max() * 0.02), f'{v:.2f}', 
                              ha='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/electricity_model_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: electricity_model_comparison.png")
    plt.close()

def plot_predictions_vs_actual(y_test, y_pred_lr, y_pred_rf, y_pred_gb):
    """Plot predictions vs actual values"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    models_data = [
        (y_pred_lr, 'Linear Regression', '#3498db'),
        (y_pred_rf, 'Random Forest', '#e74c3c'),
        (y_pred_gb, 'Gradient Boosting', '#2ecc71')
    ]
    
    for idx, (y_pred, model_name, color) in enumerate(models_data):
        axes[idx].scatter(y_test, y_pred, alpha=0.6, s=50, color=color, edgecolor='black', linewidth=0.5)
        
        # Perfect prediction line
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        axes[idx].plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, label='Perfect Prediction')
        
        axes[idx].set_xlabel('Actual Bill ($)', fontsize=11, fontweight='bold')
        axes[idx].set_ylabel('Predicted Bill ($)', fontsize=11, fontweight='bold')
        axes[idx].set_title(f'{model_name}', fontsize=12, fontweight='bold')
        axes[idx].legend()
        axes[idx].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/electricity_predictions_vs_actual.png', dpi=300, bbox_inches='tight')
    print("Saved: electricity_predictions_vs_actual.png")
    plt.close()

def plot_feature_importance(models):
    """Plot feature importance"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    feature_names = ['Month', 'Household_Size', 'House_Area_SqFt', 'Age_Of_Appliances',
                    'AC_Usage_Hours', 'Heating_Usage_Hours', 'Water_Heater_Hours',
                    'Lighting_Hours', 'Occupancy_Rate', 'Total_Consumption_kWh', 'Tariff_Rate']
    
    # Random Forest
    rf_model = models['Random Forest']
    importances = rf_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1][:8]
    axes[0].barh(np.array(feature_names)[sorted_idx], importances[sorted_idx], color='#3498db', 
                alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[0].set_title('Random Forest Feature Importance', fontsize=12, fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)
    
    # Gradient Boosting
    gb_model = models['Gradient Boosting']
    importances = gb_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1][:8]
    axes[1].barh(np.array(feature_names)[sorted_idx], importances[sorted_idx], color='#e74c3c', 
                alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[1].set_title('Gradient Boosting Feature Importance', fontsize=12, fontweight='bold')
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/electricity_feature_importance.png', dpi=300, bbox_inches='tight')
    print("Saved: electricity_feature_importance.png")
    plt.close()

def plot_appliance_impact(df):
    """Plot appliance usage impact on bills"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # AC usage impact
    ac_bins = pd.cut(df['AC_Usage_Hours'], bins=5)
    ac_bill = df.groupby(ac_bins)['Monthly_Bill'].mean()
    axes[0, 0].bar(range(len(ac_bill)), ac_bill.values, color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0, 0].set_xlabel('AC Usage Hours (Binned)', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Average Bill ($)', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('AC Usage Impact on Monthly Bill', fontsize=12, fontweight='bold')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Heating usage impact
    heating_bins = pd.cut(df['Heating_Usage_Hours'], bins=5)
    heating_bill = df.groupby(heating_bins)['Monthly_Bill'].mean()
    axes[0, 1].bar(range(len(heating_bill)), heating_bill.values, color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0, 1].set_xlabel('Heating Usage Hours (Binned)', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Average Bill ($)', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Heating Usage Impact on Monthly Bill', fontsize=12, fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # House area impact
    area_bins = pd.cut(df['House_Area_SqFt'], bins=5)
    area_bill = df.groupby(area_bins)['Monthly_Bill'].mean()
    axes[1, 0].bar(range(len(area_bill)), area_bill.values, color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1, 0].set_xlabel('House Area (Sq Ft) (Binned)', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Average Bill ($)', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('House Area Impact on Monthly Bill', fontsize=12, fontweight='bold')
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Appliance age impact
    age_bins = pd.cut(df['Age_Of_Appliances'], bins=5)
    age_bill = df.groupby(age_bins)['Monthly_Bill'].mean()
    axes[1, 1].bar(range(len(age_bill)), age_bill.values, color='#f39c12', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1, 1].set_xlabel('Appliance Age (Years) (Binned)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Average Bill ($)', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Appliance Age Impact on Monthly Bill', fontsize=12, fontweight='bold')
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/electricity_appliance_impact.png', dpi=300, bbox_inches='tight')
    print("Saved: electricity_appliance_impact.png")
    plt.close()

def main():
    print("="*80)
    print("MONTHLY ELECTRICITY BILL PREDICTION SYSTEM")
    print("="*80)
    
    # Generate dataset
    print("\n[1] Generating electricity consumption data...")
    df = generate_electricity_data(n_samples=1200)
    df.to_csv('/home/ubuntu/electricity_consumption_data.csv', index=False)
    print(f"Dataset generated: {len(df)} records")
    print(f"Average monthly bill: ${df['Monthly_Bill'].mean():.2f}")
    print(f"Average consumption: {df['Total_Consumption_kWh'].mean():.2f} kWh")
    
    # Prepare features
    print("\n[2] Preparing features...")
    X, y, scaler = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    
    # Train models
    print("\n[3] Training regression models...")
    models, results_df, y_test, y_pred_lr, y_pred_rf, y_pred_gb = train_models(X_train, X_test, y_train, y_test)
    results_df.to_csv('/home/ubuntu/electricity_model_results.csv', index=False)
    print("\nModel Results:")
    print(results_df.to_string(index=False))
    
    # Generate visualizations
    print("\n[4] Generating visualizations...")
    plot_consumption_distribution(df)
    plot_model_comparison(results_df)
    plot_predictions_vs_actual(y_test, y_pred_lr, y_pred_rf, y_pred_gb)
    plot_feature_importance(models)
    plot_appliance_impact(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All visualizations saved")
    print("="*80)

if __name__ == "__main__":
    main()
