from st_pages import Page, show_pages, add_page_title

# Optional -- adds the title and icon to the current page
add_page_title()

show_pages(
    [
        Page("./pages/app.py", "LLMao", "💊"),
        Page("./pages/about.py", "About", ":books:"),
        Page("./pages/disviz.py", "DisViz", "👁️")
    ]
)
