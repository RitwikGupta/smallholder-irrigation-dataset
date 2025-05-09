import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_num_images(df, title, by_survey=False):
    counts = df['operator_initials'].value_counts().sort_index()

    # if by_survey is True, we need to divide the image count by the number of unique source_file values for each operator
    if by_survey:
        surveys_per_op = (
            df
            .groupby('operator_initials')['source_file']
            .nunique()
            .sort_index()
        )
        counts = counts.div(surveys_per_op)
        

    plt.figure(figsize=(6, 4))
    sns.barplot(x=counts.index, y=counts.values)
    plt.title(title)
    plt.ylabel("Number of Images")
    plt.xlabel("Labeler")
    plt.ylim(0, max(counts.values) + 10)
    plt.show()

def plot_irrigation_distribution(df, title):
    # 1) Count how many times each operator gives each irrigation label
    counts = (
        df
        .groupby(['operator_initials','irrigation'])
        .size()
        .unstack(fill_value=0)       # rows: operator, cols: irrigation levels
    )

    # 2) Turn those into fractions *per operator*
    fracs = counts.div(counts.sum(axis=1), axis=0)  # divide each row by its row‐sum

    # 3) Transpose so x-axis is irrigation, columns are operators
    to_plot = fracs.T  # now rows: irrigation, cols: operator_initials

    # 4) Plot
    ax = to_plot.plot(kind='bar', figsize=(10,6))
    ax.set_xlabel("Irrigation Label (1–5)")
    ax.set_ylabel("Fraction of labels")
    ax.set_title(title)
    ax.legend(title="Labeler")
    plt.tight_layout()
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
