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
                       sliderInput("year_range", "Year Range:",
                                   min = 2016, max = 2025,
                                   value = c(2016, 2025), sep = ""),
                       selectInput("irrigation_filter", "Irrigation Status:",
                                   choices = c("All", "Yes", "No"), selected = "All"),
                       sliderInput("certainty_filter", "Min Certainty Score:", min = 1, max = 4, value = 3)
                ),
                column(9,
                       leafletOutput("irrigation_map", height = 600)
                )
              )
      )
    )
  )
)