import json
import requests
from bs4 import BeautifulSoup


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT',
          "cookie": "_ym_uid=1640026259171068384; list_mode=h; locale=zh; _ym_d=1700757977; comment_warning=1; over18=1; theme=auto; cf_clearance=klXmy09kk0227yCuMKEDDdbV7Os6QIl7VkxXCZERBSI-1722153133-1.0.1.1-j7hZ_8GF51nuAn7iWgCG0Fq872q6.Rf5uc8FobdwQ82k_Hp5C0eWoUEEK60VlIFyUgrGdm4NsIBeWzW3TVwm1g; _jdb_session=Sq68slwV%2BuFJzyBnsRugpQ%2BYn8SNGWkejpbG%2Ft3H0ovDiMzxvZVXj%2BrnsiwB7PY1X4RzpgBA6%2FKhmjEFXXMZfXl8dKEjN22o4EpgVoqsAjA9CynkBKy%2FMdCbIIx0ssHNB536dEEluawSpc003BfNL3bNGHPhJ4C7uFSiakx8dK0USVgqNXEqlFgJAsG8LoRPQalQlgu4MfIU6YhZiF77cDTCH76357yU1tSrYmXyAZpzJ5Ea3I2VyIxeSDN21ifsoJBMEzeZLA%2F8pOwcLfxoAEP2I6Lcfl3cZhSf%2BWfkmbJhSGC0W8ePDPPIYTzjuJTugqNfQaLA9ZojKoIbvyAtWbveeqKFiAZxaRZyacrpdvYpzk9IJwFBGoDB1Jz4Q4zn2%2FA%3D--nBSXfUq3B6diVDWJ--kslETYNYfHMScfKAuA4WSw%3D%3D"

          }

# Define the base URL of the webpage
base_url = "https://javdb.com/rankings/top?page="

# List to store movie information
movies = []

# Loop through each page (1 to 7)
for page in range(1, 8):
    # Construct the URL for the current page
    url = base_url + str(page) +"&t=y2023"
    print(url)

    # Send a GET request to the webpage
    response = requests.get(url,headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the webpage content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all movie items
        movie_items = soup.find_all("div", class_="item")

        # Loop through each movie item and extract information
        for item in movie_items:
            title = item.find("div", class_="video-title").text.strip()
            ranking = item.find("span", class_="ranking").text.strip()
            cover_img = item.find("img")["src"]
            score = item.find("span", class_="value").text.strip()
            tags = [tag.text.strip() for tag in item.find_all("span", class_="tag")]

            movie_info = {
                "title": title,
                "ranking": ranking,
                "cover_img": cover_img,
                "score": score,
                "tags": tags
            }

            movies.append(movie_info)
    else:
        print(f"Failed to retrieve page {page}")

# Save the movie information to a JSON file
with open("2023top250_movies.json", "w", encoding="utf-8") as f:
    json.dump(movies, f, ensure_ascii=False, indent=4)

print("Movie information extracted and saved to top250_movies.json")

