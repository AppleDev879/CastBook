import requests
from bs4 import BeautifulSoup
import re

# URL of the webpage you want to scrape
# Replace with the actual URL
urls = ["https://www.imdb.com/title/tt14208870/fullcredits/?ref_=tt_cl_sm",
        "https://www.imdb.com/title/tt0082971/fullcredits?ref_=tt_ov_st_sm",
        "https://www.imdb.com/title/tt9603212/fullcredits?ref_=tt_ov_st_sm",
        "https://www.imdb.com/title/tt15398776/fullcredits?ref_=tt_ov_st_sm",
        "https://www.imdb.com/title/tt1517268/fullcredits?ref_=tt_ov_st_sm"
        ]

# Class name of the HTML elements you want to extract text from
class_name = "credit"  # Replace with the actual class name
texts_set = set()
for url in urls:
    # Send an HTTP GET request to the webpage
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all elements with the specified class
        elements_with_class = soup.find_all(class_=class_name)

        # Extract and store the inner text in a list
        inner_texts = [element.get_text().strip()
                       for element in elements_with_class]
        for text in inner_texts:
            if not re.match(r'\(.*\)', text):
                texts_set.add(text)

    else:
        print(f"Failed to fetch the webpage {url}")

# Join the inner texts into a single string
result_text = "\n".join(texts_set)

# Save the result to a text file
filename = './res/imdb-roles.txt'
with open(filename, "w", encoding="utf-8") as output_file:
    output_file.write(result_text)

print(
    f"Extracted text from {len(texts_set)} elements and saved to {filename}")
