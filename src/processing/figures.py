import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_num_images(df, title):
    counts = df['operator_initials'].value_counts().sort_index()

    plt.figure(figsize=(6, 4))
    sns.barplot(x=counts.index, y=counts.values)
    plt.title(title)
    plt.ylabel("Number of Images")
    plt.xlabel("Labeler")
    plt.ylim(0, max(counts.values) + 10)
    plt.show()

def plot_irrigation_distribution(df, title):
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x="irrigation", hue="operator_initials")
    plt.title(title)
    plt.xlabel("Irrigation Label (1-5)")
    plt.ylabel("Count")
    plt.legend(title="Labeler")
    plt.show()

def plot_percent_coverage(df, title, certain_only=False, ymax=None):
    plt.figure(figsize=(10, 6))
    if certain_only == True:
        yvar = "percent_coverage_high_certainty"
    else:
        yvar = "percent_coverage"
    sns.boxplot(data=df, x="operator_initials", y=yvar)
    plt.title(title)
    plt.xlabel("Labeler")
    plt.ylabel("Percent Area Covered")
    if ymax:
        plt.ylim(0, ymax)
    plt.show()

def plot_avg_polygon_size(df, title, certain_only=False, ymax=None):
    plt.figure(figsize=(10, 6))
    if certain_only == True:
        yvar = df["poly_avg_size_high_certainty"].apply(np.sqrt)
    else:
        yvar = df["poly_avg_size"].apply(np.sqrt)
    sns.boxplot(data=df, x="operator_initials", y=yvar)
    plt.title(title)
    plt.xlabel("Labeler")
    plt.ylabel("Average polygon size sqrt(m^2)")
    if ymax:
        plt.ylim(0, ymax)
    plt.show()
