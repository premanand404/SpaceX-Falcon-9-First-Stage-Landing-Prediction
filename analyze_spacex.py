"""EDA charts and classification comparison for the IBM SpaceX capstone."""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, jaccard_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from src.common import ROOT, OUTPUT_DIR, load_course_csv, ensure_class


def run_eda():
    df = ensure_class(load_course_csv("dataset_part_2.csv"))
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["LaunchYear"] = df["Date"].dt.year
    for col in ["PayloadMass", "FlightNumber", "Class"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "LaunchSite" in df:
        site = df.groupby("LaunchSite", dropna=False).agg(launches=("Class", "size"), success_rate=("Class", "mean")).reset_index()
        site["success_rate_pct"] = site["success_rate"] * 100
        site.to_csv(OUTPUT_DIR / "success_by_site.csv", index=False)
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(site["LaunchSite"].astype(str), site["success_rate_pct"])
        ax.set_title("Landing success rate by launch site")
        ax.set_ylabel("Successful landings (%)")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=20)
        for b, n in zip(bars, site["launches"]):
            ax.annotate(f"n={n}", (b.get_x()+b.get_width()/2, b.get_height()), ha="center", va="bottom", fontsize=9)
        fig.tight_layout(); fig.savefig(OUTPUT_DIR / "success_by_site.png", dpi=180); plt.close(fig)

    if "Orbit" in df:
        orbit = df.groupby("Orbit", dropna=False).agg(launches=("Class", "size"), success_rate=("Class", "mean")).reset_index()
        orbit["success_rate_pct"] = orbit["success_rate"] * 100
        orbit.to_csv(OUTPUT_DIR / "success_by_orbit.csv", index=False)
        fig, ax = plt.subplots(figsize=(9, 5))
        orbit = orbit.sort_values("success_rate_pct", ascending=False)
        ax.bar(orbit["Orbit"].astype(str), orbit["success_rate_pct"])
        ax.set_title("Landing success rate by orbit")
        ax.set_ylabel("Successful landings (%)"); ax.set_ylim(0, 100); ax.tick_params(axis="x", rotation=25)
        fig.tight_layout(); fig.savefig(OUTPUT_DIR / "success_by_orbit.png", dpi=180); plt.close(fig)

    if "LaunchYear" in df and df["LaunchYear"].notna().any():
        yearly = df.dropna(subset=["LaunchYear"]).groupby("LaunchYear").agg(launches=("Class", "size"), success_rate=("Class", "mean")).reset_index()
        yearly["success_rate_pct"] = yearly["success_rate"] * 100
        yearly.to_csv(OUTPUT_DIR / "success_by_year.csv", index=False)
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(yearly["LaunchYear"], yearly["success_rate_pct"], marker="o")
        for _, r in yearly.iterrows():
            ax.annotate(f"{r.success_rate_pct:.0f}%\n(n={int(r.launches)})", (r.LaunchYear, r.success_rate_pct), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)
        ax.set_title("First-stage landing success rate by year")
        ax.set_ylabel("Successful landings (%)"); ax.set_xlabel("Launch year"); ax.set_ylim(0, 105); ax.grid(alpha=.25)
        fig.tight_layout(); fig.savefig(OUTPUT_DIR / "success_by_year.png", dpi=180); plt.close(fig)

    if "PayloadMass" in df and "FlightNumber" in df:
        fig, ax = plt.subplots(figsize=(8, 5))
        points = ax.scatter(df["FlightNumber"], df["PayloadMass"], c=df["Class"], alpha=.8)
        ax.set_title("Payload mass vs flight number")
        ax.set_xlabel("Flight number"); ax.set_ylabel("Payload mass (kg)")
        fig.tight_layout(); fig.savefig(OUTPUT_DIR / "payload_vs_flight.png", dpi=180); plt.close(fig)

    missing = (df.isna().mean() * 100).sort_values(ascending=False).rename("missing_pct").reset_index(names="column")
    missing.to_csv(OUTPUT_DIR / "missingness_pct.csv", index=False)
    df.to_csv(OUTPUT_DIR / "modeling_data_cleaned.csv", index=False)
    print(f"EDA complete. Dataset rows: {len(df)}; outputs: {OUTPUT_DIR}")


def run_models():
    ydf = ensure_class(load_course_csv("dataset_part_2.csv"))
    X = load_course_csv("dataset_part_3.csv")
    y = pd.to_numeric(ydf["Class"], errors="coerce")
    valid = y.notna()
    X, y = X.loc[valid].copy(), y.loc[valid].astype(int)
    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True)).fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2, stratify=y)

    models = {
        "Logistic Regression": (LogisticRegression(max_iter=3000, random_state=2), {"model__C": [0.01, 0.1, 1, 10]}),
        "SVM": (SVC(random_state=2), {"model__kernel": ["linear", "rbf"], "model__C": [0.1, 1, 10], "model__gamma": ["scale", "auto"]}),
        "Decision Tree": (DecisionTreeClassifier(random_state=2), {"model__criterion": ["gini", "entropy"], "model__max_depth": [2, 4, 6, 8, None], "model__min_samples_leaf": [1, 2, 4]}),
        "KNN": (KNeighborsClassifier(), {"model__n_neighbors": [3, 5, 7, 9], "model__weights": ["uniform", "distance"], "model__p": [1, 2]}),
    }
    rows, fitted = [], {}
    for name, (estimator, params) in models.items():
        pipe = Pipeline([("scaler", StandardScaler()), ("model", estimator)])
        search = GridSearchCV(pipe, params, cv=5, scoring="accuracy", n_jobs=-1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            search.fit(X_train, y_train)
        pred = search.predict(X_test)
        rows.append({
            "model": name,
            "cv_accuracy": search.best_score_,
            "test_accuracy": accuracy_score(y_test, pred),
            "precision": precision_score(y_test, pred, zero_division=0),
            "recall": recall_score(y_test, pred, zero_division=0),
            "f1": f1_score(y_test, pred, zero_division=0),
            "jaccard": jaccard_score(y_test, pred, zero_division=0),
            "best_params": str(search.best_params_),
        })
        fitted[name] = (search, pred)
        disp = ConfusionMatrixDisplay(confusion_matrix(y_test, pred), display_labels=["Class 0", "Class 1"])
        disp.plot(cmap="Blues", colorbar=False)
        plt.title(f"{name}: held-out test confusion matrix")
        plt.tight_layout(); plt.savefig(OUTPUT_DIR / f"confusion_matrix_{name.lower().replace(' ', '_')}.png", dpi=180); plt.close()

    result = pd.DataFrame(rows).sort_values(["test_accuracy", "cv_accuracy"], ascending=False)
    result.to_csv(OUTPUT_DIR / "model_metrics.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(result)); w = .35
    ax.bar(x - w/2, result["cv_accuracy"]*100, w, label="CV accuracy")
    ax.bar(x + w/2, result["test_accuracy"]*100, w, label="Held-out test accuracy")
    ax.set_xticks(x, result["model"], rotation=15, ha="right")
    ax.set_ylim(0, 100); ax.set_ylabel("Accuracy (%)"); ax.set_title("Classifier comparison"); ax.legend()
    fig.tight_layout(); fig.savefig(OUTPUT_DIR / "model_comparison.png", dpi=180); plt.close(fig)
    print(result.to_string(index=False))
    print(f"Model metrics saved to {OUTPUT_DIR / 'model_metrics.csv'}")


if __name__ == "__main__":
    run_eda()
    run_models()
