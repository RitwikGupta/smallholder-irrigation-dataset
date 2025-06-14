# shiny_app/server.R

server <- function(input, output, session) {
  
  output$home_html <- renderUI({
    includeHTML("www/home.html")
  })
  
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
  
  output$irrigation_map <- renderLeaflet({
    leaflet() |> addTiles() |>
      addCircleMarkers(
        data = filtered_data(),
        lng = ~longitude, lat = ~latitude,
        color = ~ifelse(irrigation_present == "Yes", "green", "gray"),
        radius = ~certainty_score * 2,
        label = ~paste("ID:", label_id, "<br>Certainty:", certainty_score)
      )
  })
  
  output$irrigation_table <- renderDT({
    DT::datatable(filtered_data(), options = list(pageLength = 10))
  })
  
  output$download_csv <- downloadHandler(
    filename = function() { "irrigation_data.csv" },
    content = function(file) {
      write_csv(filtered_data(), file)
    }
  )
  
  output$image_gallery <- renderUI({
    image_files <- list.files("www/images", full.names = TRUE)
    tagList(
      lapply(image_files, function(img) {
        tags$img(src = paste0("images/", basename(img)), height = "300px", style = "margin:10px;")
      })
    )
  })
}
