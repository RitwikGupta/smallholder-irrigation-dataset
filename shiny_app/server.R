# shiny_app/server.R
# Server-side logic of the app

# This server script renders a single interactive leaflet map
# displaying irrigation points filtered by user inputs. Clicking a point
# shows metadata like ID and certainty score.

##### --- Load Libraries and Data --- #####
library(tidyverse)
library(sf)
library(leaflet)
library(viridisLite)


# Load merged irrigation dataset
# merged_data <- read_csv("data/merged_dataset.csv")

##### --- Define Server Logic --- #####
server <- function(input, output, session) {
  
################################################################
  ## MAP TAB ##
  
  ##### --- Reactive Data Filter --- #####
  filtered_data <- reactive({
    df <- summary_data 
    
    # Filter based on toggle
    if (!input$show_zero_coverage) {
      df <- df |> filter(avg_percent_coverage > 0)
    }
    
    # Filter water source status if selected
    if (input$water_source_filter != "All") {
      df <- df |> filter(as.character(water_source) == input$water_source_filter)
    }
    
    # Filter by year and certainty
    df |> filter(
      year >= input$year_range_filter[1],
      year <= input$year_range_filter[2],
      avg_certainty >= input$certainty_filter
    )
  })
  
  ##### --- Render Leaflet Map --- #####
  output$irrigation_map <- renderLeaflet({
   
     # Define color palette
    pal <- colorNumeric(
      palette = "viridis",
      domain = summary_data$log_coverage
    )
    
    # Create the leaflet map with filtered data
    leaflet(data = filtered_data()) |> 
      addProviderTiles(providers$CartoDB.Positron) |> 
      addCircleMarkers(
        # Use coordinates from the data
        lng = ~x,
        lat = ~y,
        
        # Adjust the aesthetics of each point
        color = ~ifelse(avg_percent_coverage == 0, "dimgray", pal(log_coverage)),
        radius = ~sqrt(images) * 2.5,
        stroke = FALSE, fillOpacity = 0.85,
        
        # Add popups with site ID and certainty score
        layerId = ~location_num
      ) |>
      
      # Add in a legend
    addLegend(
      pal = pal,
      values = filtered_data()$log_coverage,
      title = "Coverage (%)",
      labFormat = function(type, cuts, p) {
        paste0(round(expm1(cuts), 1), "%")
      }
    )
    
  })
  
  ##### --- Reactive: Store Selected Point --- #####
  selected_point <- reactiveVal(NULL)
  
  # Add in clicking functionality
  observeEvent(input$irrigation_map_marker_click, {
    click <- input$irrigation_map_marker_click
    if (!is.null(click$id)) {
      point_info <- filtered_data() |> filter(location_num == click$id)
      selected_point(point_info)
    }
  })
  
  ##### --- Output: Render Clicked Point Info Table --- #####
  output$site_table <- renderUI({
    req(selected_point())
    info <- selected_point()
    
    # Display information from the data on the table
    # Render the information table safely
    tags$table(class = "table table-sm",
               tags$tbody(
                 tags$tr(tags$th("Number of Images"),
                         tags$td(paste(info$images[[1]]))),
                 tags$tr(tags$th("Average Certainty"),
                         tags$td(round(as.numeric(info$avg_certainty[[1]]), 2))),
                 tags$tr(tags$th("Water Source"),
                         tags$td(as.character(info$water_source_mode[[1]]))),
                 tags$tr(tags$th("Coverage"),
                         tags$td(sprintf("%.3f%%", as.numeric(info$avg_percent_coverage[[1]])))),
                 tags$tr(tags$th("High Certainty Coverage"),
                         tags$td(sprintf("%.3f%%", as.numeric(info$avg_percent_coverage_high[[1]]))))
               )
    )
    
  })
################################################################
  ## TIME SERIES TAB ##
  ##### --- Reactive Data Filter --- #####
  observe({
    updateSelectInput(
      inputId = "province_filter",
      choices = unique(labels_df$province),
      selected = unique(labels_df$province)[1]
    )
  })
  
  ##### --- Render Time Series Plot --- #####
  output$coverage_time_series_plot <- renderPlot({
    req(input$province_filter)
    
    # Filter to selected province and high certainty labels
    df <- labels_df %>%
      filter(province == input$province_filter, irrigation_certainty >= 3) %>%
      mutate(month = floor_date(as.Date(date), "month"))
    
    # Summarize coverage
    summary_df <- df %>%
      group_by(month) %>%
      summarise(
        mean_coverage = mean(coverage_percent, na.rm = TRUE),
        se = sd(coverage_percent, na.rm = TRUE) / sqrt(n()),
        .groups = "drop"
      ) %>%
      mutate(
        lower = mean_coverage - 1.96 * se,
        upper = mean_coverage + 1.96 * se
      )
    
    # Plot
    ggplot(summary_df, aes(x = month, y = mean_coverage)) +
      geom_line(color = "darkgreen", size = 1) +
      geom_ribbon(aes(ymin = lower, ymax = upper), fill = "palegreen", alpha = 0.4) +
      labs(
        x = "Month",
        y = "Avg. % High Certainty Coverage",
        title = paste("High Certainty Irrigation Coverage in", input$province_filter),
        caption = "Shaded area = 95% CI"
      ) +
      theme_minimal() +
      scale_x_date(date_labels = "%b %Y", date_breaks = "2 months") +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
  })
  
  
################################################################
  ## CONTEXT TAB ##
  
  ##### --- Output: Render Context qmd --- #####
  output$context_html <- renderUI({
    includeHTML("www/context.html")
  })
  
  
}
