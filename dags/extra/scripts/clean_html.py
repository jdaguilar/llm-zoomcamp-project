from bs4 import BeautifulSoup
import os

# Directory containing the downloaded HTML files
html_dir = "/opt/airflow/data/docs"
cleaned_html_dir = "/opt/airflow/data/clean_docs"

# Ensure the cleaned directory exists
os.makedirs(cleaned_html_dir, exist_ok=True)


# Function to clean HTML content
def clean_html(file_path, cleaned_file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "lxml")

        # Remove unnecessary tags
        for tag in soup(
            ["script", "style", "header", "footer", "nav", "button", "link", "meta"]
        ):
            tag.decompose()

        # Loop through all elements and remove the 'class' attribute
        for element in soup.find_all(class_=True):
            del element["class"]

        # Remove all divs with the specific role
        for div in soup.find_all("div", role=["banner", "region"]):
            div.decompose()

        # Find all <div> elements with an id attribute
        for div in soup.find_all("div", id=True):
            # Remove the 'id' attribute
            del div["id"]

        # Remove all <a> tags including their contents
        # for a_tag in soup.find_all("a"):
        #     a_tag.decompose()
        # Loop through all <a> tags
        for a_tag in soup.find_all("a"):
            # Get the href attribute if it exists
            href_value = a_tag.get("href")

            # Clear all attributes of the <a> tag
            a_tag.attrs = {}

            # Restore only the href attribute
            if href_value:
                a_tag["href"] = href_value

        # Remove 'style' attribute from specific tags (div, span, p)
        for tag in soup.find_all(["div", "span", "p", "pre"]):
            if "style" in tag.attrs:
                del tag["style"]

        # List of all header tags
        header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]

        # Loop through all header tags and remove the 'id' attribute
        for header in soup.find_all(header_tags, id=True):
            del header["id"]

        # Find and remove all <svg> elements
        for svg in soup.find_all("svg"):
            svg.decompose()

        # Save cleaned HTML
        with open(cleaned_file_path, "w", encoding="utf-8") as cleaned_file:
            cleaned_file.write(str(soup))


# Walk through all files and directories
for root, dirs, files in os.walk(html_dir):
    for file_name in files:
        if file_name.endswith(".html"):
            file_path = os.path.join(root, file_name)

            # Create the corresponding cleaned file path
            relative_path = os.path.relpath(root, html_dir)
            cleaned_subdir = os.path.join(cleaned_html_dir, relative_path)
            os.makedirs(cleaned_subdir, exist_ok=True)

            cleaned_file_path = os.path.join(cleaned_subdir, file_name)

            # Clean the HTML file
            clean_html(file_path, cleaned_file_path)
