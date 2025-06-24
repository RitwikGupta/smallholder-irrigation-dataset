# Combined Datasets
# Script for the Shiny App to take all these .csv and .geoson files and combine them into one dataset
# NOTE: This script is run locally BEFORE deployment to shinyapps.io.
# It prepares shiny_app/data/merged_dataset.csv used by the live app.

# combine_datasets.R
library(tidyverse)

# Locate all individual _merged.csv files
csv_files <- list.files(
  path = "data/labels/labeled_surveys/random_sample/merged/",
  pattern = "_merged\\.csv$", full.names = TRUE
)

# Combine them
merged_data <- purrr::map_dfr(csv_files, read_csv)

# Ensure output directory exists
dir.create("shiny_app/data", showWarnings = FALSE, recursive = TRUE)

# Save the combined dataset
write_csv(merged_data, "shiny_app/data/merged_dataset.csv")


