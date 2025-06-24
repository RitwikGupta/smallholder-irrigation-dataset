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
  dashboardHeader(title = "Zambia Irrigation Explorer"),
  
  ##### --- Sidebar Navigation Menu (Single Tab for Now) --- #####
  dashboardSidebar(
    sidebarMenu(
      id = "tabs",
      menuItem("Map Viewer", tabName = "map", icon = icon("map"))
    )
  ),
  
  ##### --- Main Body Content (Single Map Tab) --- #####
  dashboardBody(
    useShinyjs(),
    tabItems(
      tabItem(tabName = "map",
              fluidRow(
                column(3,
                       h3("Filter Images"),
                       sliderInput("year_range_filter", "Year Range:",
                                   min = 2016, max = 2025,
                                   value = c(2016, 2025), sep = ""),
                       sliderInput("certainty_filter", "Min Certainty Score:", min = 1, max = 5, value = 4),
                       selectInput("water_source_filter", "Water Source?",
                                   choices = c("All", "TRUE", "FALSE"), selected = "All"),
                       br(),
                       h3("Selected Site Details"),
                       uiOutput("site_table")
                ),
                column(9,
                       leafletOutput("irrigation_map", height = 600)
                )
              )
      )
    )
  )
)