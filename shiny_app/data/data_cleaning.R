# Prepare Merged Data
# This script cleans and prepares the data for use in the Shiny App

library(dplyr)

### --- Map Data --- ###

# Load the map data
raw <- read_csv("shiny_app/data/merged_dataset.csv")

# Check to see if site_id corresponds to unique lat / lon locations
raw |>
  group_by(site_id) |>
  summarise(n_unique_coords = n_distinct(paste(x, y))) |>
  filter(n_unique_coords > 1)
    # The tibble returned no rows, so we can confirm that site_id corresponds to unique lat/lon locations

# Removing unwanted columns
raw_clean <- raw |>
  select(-c(internal_id, plot_file, operator, source_file)) |>
  # Extract the numeric ID for each location
  mutate(location_num = as.integer(gsub("id_", "", site_id))) |>
  # Drop ID name
  select(-site_id)

# Group by location and average the percent cover values
summary_data <- raw_clean |>
  group_by(location_num, x, y) |>
  summarise(
    images = max(image_number, na.rm = TRUE),
    year = first(year),
    month = first(month),
    day = first(day),
    avg_certainty = mean(irrigation, na.rm = TRUE),
    avg_percent_coverage = mean(percent_coverage, na.rm = TRUE),
    avg_percent_coverage_high = mean(percent_coverage_high_certainty, na.rm = TRUE),
    n_labelers = n_distinct(operator_initials),
    water_source_mode = names(sort(table(water_source), decreasing = TRUE))[1],
    .groups = "drop"
  )

# Add a new column for log transform to visualize coverage easier
summary_data <- summary_data |>
  mutate(log_coverage = if_else(
    avg_percent_coverage == 0,
    0,
    log1p(avg_percent_coverage)
  ))

# Save the cleaned summary data to a CSV file for use in the Shiny app
write_csv(summary_data, "shiny_app/data/summary_data.csv")


