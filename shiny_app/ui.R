# shiny_app/ui.R

library(shinydashboard)
library(shiny)
library(shinyjs)

ui <- dashboardPage(
  skin = "blue",
  dashboardHeader(title = "Zambia Irrigation Explorer"),
  dashboardSidebar(
    sidebarMenu(
      id = "tabs",
      menuItem("Home", tabName = "home", icon = icon("info-circle")),
      menuItem("Map Viewer", tabName = "map", icon = icon("map")),
      menuItem("Data Explorer", tabName = "data", icon = icon("table")),
      menuItem("Sample Images", tabName = "images", icon = icon("image"))
    )
  ),
  dashboardBody(
    useShinyjs(),
    tabItems(
      tabItem(tabName = "home", uiOutput("home_html")),
      tabItem(tabName = "map",
              fluidRow(
                column(3,
                       sliderInput("year_range", "Year Range:",
                                   min = min(merged_data$year, na.rm = TRUE),
                                   max = max(merged_data$year, na.rm = TRUE),
                                   value = range(merged_data$year, na.rm = TRUE),
                                   sep = ""),
                       selectInput("irrigation_filter", "Irrigation Status:",
                                   choices = c("All", "Yes", "No"), selected = "All"),
                       sliderInput("certainty_filter", "Min Certainty Score:", min = 1, max = 4, value = 3)
                ),
                column(9,
                       leafletOutput("irrigation_map", height = 600)
                )
              )
      ),
      tabItem(tabName = "data",
              fluidRow(
                column(12,
                       DT::DTOutput("irrigation_table"),
                       downloadButton("download_csv", "Download CSV")
                )
              )
      ),
      tabItem(tabName = "images",
              h3("Example Annotated Sites"),
              uiOutput("image_gallery")
      )
    )
  )
)
