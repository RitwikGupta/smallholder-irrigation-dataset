# shiny_app/server.R
# Server-side logic of the app

# This server script renders a single interactive leaflet map
# displaying irrigation points filtered by user inputs. Clicking a point
# shows metadata like ID and certainty score.

##### --- Load Libraries and Data --- #####
library(tidyverse)
library(sf)
library(leaflet)

# Load merged irrigation dataset
merged_data <- read_csv("data/merged_dataset.csv")

##### --- Define Server Logic --- #####
server <- function(input, output, session) {
  
  ##### --- Reactive Data Filter --- #####
  filtered_data <- reactive({
    df <- merged_data
    if (input$irrigation_filter != "All") {
      df <- df |> filter(irrigation_present == input$irrigation_filter)
    }
    df |> filter(
      year >= input$year_range[1],
      year <= input$year_range[2],
      certainty_score >= input$certainty_filter
    )
  })
  
  ##### --- Render Leaflet Map --- #####
  output$irrigation_map <- renderLeaflet({
    leaflet(data = filtered_data()) |> 
      addProviderTiles(providers$CartoDB.Positron) |> 
      addCircleMarkers(
        lng = ~longitude,
        lat = ~latitude,
        color = ~ifelse(irrigation_present == "Yes", "green", "gray"),
        radius = ~certainty_score * 2,
        stroke = FALSE, fillOpacity = 0.8,
        label = ~paste0("Label ID: ", label_id, "<br>",
                        "Year: ", year, "<br>",
                        "Certainty: ", certainty_score, "<br>",
                        "Irrigation: ", irrigation_present),
        labelOptions = labelOptions(direction = "auto")
      )
  })
  
}
