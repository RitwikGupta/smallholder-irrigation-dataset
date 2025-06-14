# shiny_app/global.R

# Load libraries
library(shiny)
library(shinydashboard)
library(tidyverse)
library(sf)
library(leaflet)
library(DT)
library(plotly)
library(bslib)
library(shinyjs)

# Load placeholder data
# Replace these paths with real data files when ready
merged_data <- read_csv("data/merged_dataset.csv", show_col_types = FALSE)
irrigation_polygons <- st_read("data/irrigation_polygons.geojson", quiet = TRUE)
