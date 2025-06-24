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
    # Filter water source status if selected
    if (input$water_source_filter != "All") {
      df <- df |> filter(as.character(water_source) == input$water_source_filter)
    }
    
    # Filter by year and certainty
    df |> filter(
      year >= input$year_range_filter[1],
      year <= input$year_range_filter[2],
      as.numeric(irrigation) >= input$certainty_filter
    )
  })
  
  ##### --- Render Leaflet Map --- #####
  output$irrigation_map <- renderLeaflet({
    leaflet(data = filtered_data()) |> 
      addProviderTiles(providers$CartoDB.Positron) |> 
      addCircleMarkers(
        lng = ~x,
        lat = ~y,
        color = "steelblue",
        radius = ~sqrt(percent_coverage_high_certainty) * 5,
        stroke = FALSE, fillOpacity = 0.8,
        layerId = ~site_id
      )
  })
  
  ##### --- Reactive: Store Selected Point --- #####
  selected_point <- reactiveVal(NULL)
  
  observeEvent(input$irrigation_map_marker_click, {
    click <- input$irrigation_map_marker_click
    if (!is.null(click$id)) {
      point_info <- filtered_data() |> filter(site_id == click$id)
      selected_point(point_info)
    }
  })
  
  ##### --- Output: Render Clicked Point Info Table --- #####
  output$site_table <- renderUI({
    req(selected_point())
    info <- selected_point()
    
    tags$table(class = "table table-sm",
               tags$tbody(
                 tags$tr(tags$th("Image Date"), tags$td(paste(info$year[[1]], info$month[[1]], info$day[[1]], sep = "-"))),
                 tags$tr(tags$th("Operator"), tags$td(as.character(info$operator_initials[[1]]))),
                 tags$tr(tags$th("Certainty"), tags$td(as.character(info$irrigation[[1]]))),
                 tags$tr(tags$th("Water Source"), tags$td(as.character(info$water_source[[1]]))),
                 tags$tr(tags$th("Coverage"), tags$td(sprintf("%.3f%%", info$percent_coverage[[1]]))),
                 tags$tr(tags$th("High Certainty Coverage"), tags$td(sprintf("%.3f%%", info$percent_coverage_high_certainty[[1]])))
               )
    )
  })
  
  
  
  
  
}
