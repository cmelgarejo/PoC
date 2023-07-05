import asyncio
import aiohttp
import re
import os
from dotenv import load_dotenv
import boto3
import json
from bs4 import BeautifulSoup

load_dotenv()

aws_access_key_id = value = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = value = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")  # Specify the AWS region

s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region,
)

# Specify the S3 bucket and file name
bucket_name = os.getenv("BUCKET_NAME")


async def scrape_products(link):
    async with aiohttp.ClientSession() as session:
        # Start the loop
        next_link = link

        # Set the counter variable and limit
        counter = 0
        limit_next_links = 3  # just get 3 pages for testing purposes

        # Continue scraping next pages if available and within the limit
        while next_link and counter < limit_next_links:
            # Find the link to the next page
            async with session.get(next_link) as response:
                next_soup = BeautifulSoup(await response.text(), "html.parser")
                # Find the next link in the html
                next_link = find_next_link(next_soup)
                await parse_product_list(counter + 1, next_soup, session)

            # Increment the counter
            counter += 1


async def scrape_product_page(page, product_link, session):
    # Send a GET request to the product page
    async with session.get(product_link) as response:
        product_soup = BeautifulSoup(await response.text(), "html.parser")

    # Extract data from the product page
    return parse_product_page(product_soup)


def find_next_link(soup):
    # Find the link with rel="next"
    link = soup.find("a", attrs={"rel": "next"})

    if link:
        # print("NEXT LINK: {link}".format(link=link))
        return link["href"]

    return None


async def parse_product_list(page, soup, session):
    # Find the div elements containing the links to the products
    divs = soup.find_all("div", class_="result-table-row-txt")

    tasks = []
    # Iterate over each div element
    for div in divs:
        # Find the link within the div with the text "View Details"
        link_cell = div.find("a", string="View Details")
        if link_cell:
            product_link = link_cell["href"]
            print(product_link)
            tasks.append(scrape_product_page(page, product_link, session))

    # Wait for all tasks to complete
    product_data_list = await asyncio.gather(*tasks)

    # Process the extracted data as needed
    process_data(page, product_data_list)


# Process the product page and extract data
def parse_product_page(soup):
    # Find the section element with class="details-area"
    section = soup.find("section", class_="details-area")

    # Find all divs with class="prd-des-lis" within the section
    divs = section.find_all("div", class_="prd-des-lis")

    # Create a dictionary to store the extracted data
    product_data = {}

    # Iterate over each div element
    for div in divs:
        # Ignore divs with the "hidden" class
        if "hidden-md" in div.get("class", []):
            continue

        # Find the nested div with class="col-lg-12 col-md-12 col-sm-12 col-xs-12"
        inner_div = div.find("div", class_="col-lg-12 col-md-12 col-sm-12 col-xs-12")
        if inner_div is None:
            continue

        # Find the nested div with class="row" inside the inner div
        row_div = inner_div.find("div", class_="row")
        if row_div is None:
            continue

        # Find the two nested divs inside the row div
        label_div = row_div.find(
            "div", class_="col-lg-4 col-md-4 col-sm-12 col-xs-12 prod-categorty"
        )
        data_div = row_div.find(
            "div",
            class_="col-lg-8 col-md-8 col-sm-12 col-xs-12 clearfix prod-categorty prod-category-back",
        )
        if data_div is None:
            data_div = row_div.find(
                "p",
                id="productSynonymText",
            )

        # Extract the label and data from the corresponding divs
        label = label_div.text.strip()
        data = data_div.text.strip()
        data = re.sub(r" {2,}|\r|\n", "", data)
        # print("label: {label}".format(label=label))
        # print("data: {data}".format(data=data))

        # Store the extracted data in the product_data dictionary
        product_data[label] = data

    return product_data


# Process the extracted data
def process_data(page, data):
    file_name = f"page-{page}.json"
    json_data = json.dumps(data, indent=4)
    # Upload the JSON file to S3
    s3.put_object(Body=json_data, Bucket=bucket_name, Key=file_name)


# Example usage
link_to_table = "https://www.parchem.com/raw-material-chemicals-supplier-distributor.aspx"
loop = asyncio.get_event_loop()
loop.run_until_complete(scrape_products(link_to_table))
