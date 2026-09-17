# The Accessibility Police
# An Automated Website Accessibility Checker

# This program analyzes a website's HTML to identify common accessibility issues
# based on selected WCAG guidelines. It checks for issues like missing page titles, 
# missing language information, missing image alt text, forms without labels, unclear
# links, and problematic heading structures. The program explains each issue and its
# potential impact on users.

import requests
from bs4 import BeautifulSoup


def get_webpage(url):
    # Retrieve website
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_html(html):
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def check_page_title(soup):
    # Check for a non-empty <title> (WCAG 2.4.2)
    
    title = soup.find('title')

    if title is None or not title.text.strip():
        return {
            "type": "Missing page title",
            "severity": "High",
            "element": str(title) if title else "None",
            "description": "The website doesn't have a title or the title is empty.",
            "user_impact": "Users may have difficulty identifying the page in search results or browser tabs."
        }

def check_images(soup):
    # Find images missing alt text (WCAG 1.1.1)
    # Success Criterion 1.1.1: All non-text content that is presented to the user has a text alternative that serves the equivalent purpose.
    
    images = soup.find_all('img')
    issues = []

    for img in images:
        if not img.has_attr("alt"):
            issues.append({
                "type": "Missing alt text",
                "severity": "High",
                "element": str(img),
                "description": "An image is missing an alt text attribute.",
                "user_impact": "Users who rely on screen readers won't know what the image represents."
            })

    return issues

def check_forms(soup):
    # Find form inputs without labels (WCAG 1.3.1, 3.3.2)
    # Success Criterion 1.3.1: Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.
    # Success Criterion 3.3.2: Labels or instructions are provided when content requires user input.
    forms = soup.find_all("form")
    issues = []

    for form in forms:
        inputs = form.find_all("input")

        for input_field in inputs:
            input_id = input_field.get("id")
            if not input_id or not form.find("label", {"for": input_id}):
                issues.append({
                    "type": "Form input without label",
                    "severity": "High",
                    "element": str(input_field),
                    "description": "A form input is missing an associated label.",
                    "user_impact": "Users who rely on screen readers might not know what information the form is asking them to enter."
                })

    return issues

def check_headings(soup):
    # Check heading structure (WCAG 1.3.1)
    # Success Criterion 1.3.1: Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    issues = []
    previous_level = 0

    for heading in headings:
        current_level = int(heading.name[1])
        if previous_level and current_level > previous_level + 1:
            issues.append({
                "type": "Incorrect heading structure",
                "severity": "Medium",
                "element": str(heading),
                "description": "Heading level " + str(current_level) + " follows heading level " + str(previous_level) + ", which may confuse users.",
                "user_impact": "Users who rely on screen readers might have difficulty understanding the content hierarchy."
            })
        previous_level = current_level

    return issues

def check_links(soup):
    # Check for empty or unclear links (WCAG 2.4.4)
    # Success Criterion 2.4.4: The purpose of each link can be determined from the link text alone or from the link text together with its programmatically determined link context, except where the purpose of the link would be ambiguous to users in general.
    links = soup.find_all('a')
    issues = []
    for link in links:
        link_text = link.get_text(strip=True)
        if link_text == "":
            issues.append({
                "type": "Empty link",
                "severity": "Medium",
                "element": str(link),
                "description": "There's a link that exists but has no text content.",
                "user_impact": "Users who rely on screen readers might not know the purpose of the link."
            })
    return issues

def check_language(soup):
    # Check for missing language attribute (WCAG 3.1.1)
    # Success Criterion 3.1.1: The default human language of each web page can be programmatically determined.
    pass

def analyze_page(soup):
    # Run all accessibility checks and return a list of issues found
    pass

def display_results(results):
    # Display all findings through the CLI
    pass

def get_user_input():
    # Get the website URL from the user
    url = input("Enter the website URL: ")
    return url


# Testing
html = get_webpage("https://beautiful-soup-4.readthedocs.io/en/latest/")
soup = parse_html(html)

url = get_user_input()
print ("Website entered: " + url)