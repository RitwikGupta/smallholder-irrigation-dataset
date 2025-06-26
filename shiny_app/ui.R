# shiny_app/ui.R
# UI side logic of the app

# This script defines a simplified version of the UI layout for the Zambia Irrigation Explorer Shiny app.
# For now, it includes only a single tab for the interactive map, using shinydashboard to allow expansion later.

library(shiny)
library(shinydashboard)
library(shinyjs)
library(leaflet)

ui <- dashboardPage(
  skin = "blue",
  
  ##### --- Header --- #####
  dashboardHeader(
    title = tags$div(
      style = "display: flex; align-items: center; white-space: normal; line-height: 1.2;",
      
      tags$img(
        src = "logo.png",  # ✅ your Zambia outline image
        height = "40px",
        style = "margin-right: 10px;"
      ),
      
      tags$div(
        HTML("Irrigation Across<br>Zambia"),
        style = "font-size: 20px; font-weight: bold;"
      )
    ),
    titleWidth = 250  # ✅ Expand header width to fit the full text
  )
  
  ,
  
  ##### --- Sidebar Navigation Menu --- #####
  dashboardSidebar(
    width = 250,  # ✅ Set a fixed width for the sidebar
    sidebarMenu(
      id = "tabs",
      
      # Map Viewer Tab shows up first
      menuItem("Map Viewer", tabName = "map", icon = icon("map")),
      
      # Context tab is below
      menuItem("About the Data", tabName = "context", icon = icon("book"))
    )
  ),
  
  ##### --- Main Body Content --- #####
  dashboardBody(
    useShinyjs(),
    tabItems(
      
      ## Map Viewer Tab ##
      tabItem(tabName = "map",
              fluidRow(
               
                 # Show filters and data tables
                column(3,
                       h3("Filter Images"),
                       
                       # Add in the year slider
                       sliderInput("year_range_filter", "Year Range:",
                                   min = 2016, max = 2025,
                                   value = c(2016, 2025), sep = ""),
                       
                       # Add in the certainty slider
                       sliderInput("certainty_filter", "Min Certainty Score:", min = 1, max = 5, value = 4),
                       
                       # Add the water source selection
                       selectInput("water_source_filter", "Water Source?",
                                   choices = c("All", "TRUE", "FALSE"), selected = "All"),
                       br(),
                       
                       # Header for point table info
                       h3("Selected Site Details"),
                       uiOutput("site_table")
                ),
                
                # Show the map on the side of the filters 
                column(9,
                       leafletOutput("irrigation_map", height = 600)
                )
              )
      ),
      
      ## Context Tab ##
      tabItem(tabName = "context",
              uiOutput("context_html")
      )
    )
  )
)