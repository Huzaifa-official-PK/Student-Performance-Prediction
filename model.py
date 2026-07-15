# ==========================================================
# Student Performance Prediction System
# Model Training Script - Part 1
# Project: Student Performance Prediction
# ==========================================================

# ==========================
# Import Libraries
# ==========================
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import AdaBoostRegressor
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.impute import SimpleImputer

from sklearn.model_selection import (
    train_test_split,
    cross_val_score
)

from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

# Models

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    ExtraTreesRegressor
)

from xgboost import XGBRegressor

# ==========================================================
# Create models folder
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# ==========================================================
# Dataset Path
# ==========================================================

DATA_PATH = BASE_DIR / "data" / "StudentPerformanceFactors.csv"

print("=" * 60)
print("Loading Dataset...")
print("=" * 60)

# ==========================================================
# Read Dataset
# ==========================================================

df = pd.read_csv(DATA_PATH)

print("\nDataset Loaded Successfully.")
print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

# ==========================================================
# Display Information
# ==========================================================

print("\nDataset Information\n")
print(df.info())

print("\nFirst Five Records\n")
print(df.head())

# ==========================================================
# Remove Duplicate Records
# ==========================================================

duplicates = df.duplicated().sum()

print(f"\nDuplicate Records : {duplicates}")

if duplicates > 0:
    df.drop_duplicates(inplace=True)
    print("Duplicates Removed Successfully.")

# ==========================================================
# Missing Values
# ==========================================================

print("\nMissing Values\n")
print(df.isnull().sum())

# ==========================================================
# Target Column
# ==========================================================

TARGET = "Exam_Score"

if TARGET not in df.columns:
    raise Exception(f"{TARGET} column not found.")

# ==========================================================
# Features & Target
# ==========================================================

X = df.drop(TARGET, axis=1)
y = df[TARGET]

print("\nTarget Column :", TARGET)

# ==========================================================
# Detect Feature Types
# ==========================================================

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numerical_features = X.select_dtypes(
    exclude=["object"]
).columns.tolist()

print("\nCategorical Features")
print(categorical_features)

print("\nNumerical Features")
print(numerical_features)

# ==========================================================
# Numerical Pipeline
# ==========================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)

# ==========================================================
# Categorical Pipeline
# ==========================================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)

# ==========================================================
# Combine Pipelines
# ==========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numeric_pipeline,
            numerical_features
        ),
        (
            "cat",
            categorical_pipeline,
            categorical_features
        )
    ]
)

# ==========================================================
# Train Test Split
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining Samples :", X_train.shape[0])
print("Testing Samples  :", X_test.shape[0])

print("\nData Preprocessing Completed Successfully.")
print("=" * 60)
# ==========================================================
# MODEL TRAINING - PART 2
# ==========================================================

print("\n" + "=" * 60)
print("TRAINING MACHINE LEARNING MODELS")
print("=" * 60)

# ==========================================================
# Models Dictionary
# ==========================================================

models = {

    "Linear Regression": LinearRegression(),

    "Random Forest": RandomForestRegressor(
        n_estimators=300,
        random_state=42
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.05,
        random_state=42
    ),

    "Extra Trees": ExtraTreesRegressor(
        n_estimators=500,
        random_state=42
    ),

    "AdaBoost": AdaBoostRegressor(
        n_estimators=300,
        random_state=42
    ),

    "XGBoost": XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
        objective="reg:squarederror"
    )

}

# ==========================================================
# Variables
# ==========================================================

results = []

best_model = None
best_pipeline = None
best_score = -999

# ==========================================================
# Train Every Model
# ==========================================================

for name, model in models.items():

    print("\n" + "-" * 60)
    print(f"Training : {name}")
    print("-" * 60)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    grid_search = GridSearchCV(

        estimator=pipeline,

        param_grid=param_grids[name],

        scoring="r2",

        cv=5,

        n_jobs=-1,

        verbose=1

    )

    grid_search.fit(X_train, y_train)

    best_pipe = grid_search.best_estimator_

    predictions = best_pipe.predict(X_test)

    r2 = r2_score(y_test, predictions)

    mae = mean_absolute_error(y_test, predictions)

    mse = mean_squared_error(y_test, predictions)

    rmse = np.sqrt(mse)

    cv_score = cross_val_score(

        best_pipe,

        X,

        y,

        cv=5,

        scoring="r2"

    ).mean()

    print(f"Best Parameters : {grid_search.best_params_}")
    print(f"R2 Score        : {r2:.4f}")
    print(f"Cross Validation: {cv_score:.4f}")
    print(f"MAE             : {mae:.4f}")
    print(f"RMSE            : {rmse:.4f}")

    results.append({

        "Model": name,

        "R2": r2,

        "CV": cv_score,

        "MAE": mae,

        "RMSE": rmse

    })

    if r2 > best_score:

        best_score = r2

        best_model = name

        best_pipeline = best_pipe

# ==========================================================
# Results DataFrame
# ==========================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(

    by="R2",

    ascending=False

)

print("\n" + "=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

print(results_df)

print("\nBest Model :", best_model)

print("Best R2 Score :", round(best_score, 4))

print("=" * 60)
# ==========================================================
# MODEL TRAINING - PART 3
# Save Model & Generate Final Report
# ==========================================================

print("\n" + "=" * 60)
print("SAVING TRAINED MODEL")
print("=" * 60)

# ==========================================================
# Save Best Pipeline
# ==========================================================

MODEL_PATH = MODEL_DIR / "model.pkl"

joblib.dump(best_pipeline, MODEL_PATH)

print(f"\nBest model saved successfully.")
print(f"Location : {MODEL_PATH}")

# ==========================================================
# Save Preprocessor Separately (Optional)
# ==========================================================

PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"

joblib.dump(preprocessor, PREPROCESSOR_PATH)

print(f"Preprocessor saved successfully.")
print(f"Location : {PREPROCESSOR_PATH}")

# ==========================================================
# Final Prediction
# ==========================================================

y_pred = best_pipeline.predict(X_test)

# ==========================================================
# Final Metrics
# ==========================================================

final_r2 = r2_score(y_test, y_pred)

final_mae = mean_absolute_error(y_test, y_pred)

final_mse = mean_squared_error(y_test, y_pred)

final_rmse = np.sqrt(final_mse)

# ==========================================================
# Training Summary
# ==========================================================

print("\n" + "=" * 60)
print("FINAL TRAINING REPORT")
print("=" * 60)

print(f"Dataset Shape        : {df.shape}")

print(f"Training Samples     : {len(X_train)}")

print(f"Testing Samples      : {len(X_test)}")

print(f"Best Model           : {best_model}")

print(f"R2 Score             : {final_r2:.4f}")

print(f"Mean Absolute Error  : {final_mae:.4f}")

print(f"Root Mean Sq Error   : {final_rmse:.4f}")

print("=" * 60)

# ==========================================================
# Feature Importance
# ==========================================================

print("\nCalculating Feature Importance...")

try:
    model = best_pipeline.named_steps["model"]

    if hasattr(model, "feature_importances_"):
        feature_names = (
            best_pipeline.named_steps["preprocessor"]
            .get_feature_names_out()
        )
        importance = model.feature_importances_

        feature_df = pd.DataFrame({
            "Feature": feature_names,
            "Importance": importance
        })

        feature_df = feature_df.sort_values(
            by="Importance",
            ascending=False
        )

        print("\nTop 15 Important Features\n")
        print(feature_df.head(15))

        feature_df.to_csv(
            MODEL_DIR / "feature_importance.csv",
            index=False
        )

        print("\nFeature importance saved.")
    else:
        print("\nFeature importance is not available for this model.")

except Exception as e:
    print(e)

# ==========================================================
# Save Training Results
# ==========================================================

results_df.to_csv(
    MODEL_DIR / "model_results.csv",
    index=False
)

print("\nModel comparison saved.")

# ==========================================================
# Finished
# ==========================================================

print("\n" + "=" * 60)

print("PROJECT TRAINING COMPLETED SUCCESSFULLY")

print("=" * 60)

print("\nGenerated Files")

print("---------------------------")

print("models/model.pkl")

print("models/preprocessor.pkl")

print("models/model_results.csv")

print("models/feature_importance.csv")

print("\nReady For Flask Deployment")

print("=" * 60)