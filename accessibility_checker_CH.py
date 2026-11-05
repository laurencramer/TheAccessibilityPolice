# The Accessibility Police
# An Automated Website Accessibility Checker

# This program analyzes a website's HTML to identify common accessibility issues
# based on selected WCAG guidelines. It checks for issues like missing page titles, 
# missing language information, missing image alt text, forms without labels, unclear
# links, and problematic heading structures. The program explains each issue and its
# potential impact on users.

import requests
from bs4 import BeautifulSoup
from fast_a11y import fast_a11y

# put the URLs of your test bad sites here:


# CH
# Some sites reject the default python-requests User-Agent
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
# CH

def get_webpage(url):
    # Retrieve website
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        response = requests.get(url, timeout=10, headers=REQUEST_HEADERS)
        response.raise_for_status()
        return response.text
    # Handles a few exceptions that I ran into while testing the program. I will add more as I encounter them.
    except requests.exceptions.SSLError as error:
        print("SSL error: Unable to securely connect to this website.")
        print(error)
        return None
    except requests.exceptions.HTTPError as error:
        print("HTTP error: The website refused the request.")
        print(error)
        return None
# CH
    except requests.exceptions.RequestException as error:
        print("Request error: Unable to retrieve this website.")
        print(error)
        return None
# CH

def parse_html(html):
    # Parse HTML with BeautifulSoup
    
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def check_page_title(soup):
    # Check for a non-empty <title> (WCAG 2.4.2)
    
    issues = []
    title = soup.find('title')

    if title is None or not title.text.strip():
        issues.append({
            "type": "Missing page title",
            "severity": "High",
            "element": str(title) if title else "No specific HTML element found",
            "description": "The website doesn't have a title or the title is empty.",
            "user_impact": "Users may have difficulty identifying the page in search results or browser tabs.",
            "wcag": "2.4.2"
        })

    return issues

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
                "user_impact": "Users who rely on screen readers won't know what the image represents.",
                "wcag": "1.1.1"
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
            input_type = input_field.get("type")
            aria_label = input_field.get('aria-label')
            title = input_field.get('title')
            value = input_field.get('value')
            if input_type == "hidden":
                continue
            if (not input_id or not form.find("label", {"for": input_id})) and not aria_label and not title and not value:
                issues.append({
                    "type": "Form input without label",
                    "severity": "High",
                    "element": str(input_field),
                    "description": "A form input is missing an associated label.",
                    "user_impact": "Users who rely on screen readers might not know what information the form is asking them to enter.",
                    "wcag": "1.3.1, 3.3.2"
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
                "user_impact": "Users who rely on screen readers might have difficulty understanding the content hierarchy.",
                "wcag": "1.3.1"
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
        aria_label = link.get('aria-label')
        aria_labelledby = link.get('aria-labelledby')
        title = link.get('title')
        image = link.find('img')
        svg = link.find('svg')
        svg_label = svg.get('aria-label') if svg else None
        image_alt = image.get('alt') if image else None
        if link_text == "" and (aria_label is None or aria_label.strip() == "") and (aria_labelledby is None or aria_labelledby.strip() == "") and (svg_label is None or svg_label.strip() == "") and (title is None or title.strip() == "") and (image_alt is None or image_alt.strip() == ""):
            issues.append({
                "type": "Empty link",
                "severity": "Medium",
                "element": str(link),
                "description": "There's a link that exists but has no text content.",
                "user_impact": "Users who rely on screen readers might not know the purpose of the link.",
                "wcag": "2.4.4"
            })
    return issues

def check_language(soup):
    # Check for missing language attribute (WCAG 3.1.1)
    # Success Criterion 3.1.1: The default human language of each web page can be programmatically determined.
    
    language = soup.find('html').get('lang')
    issues = []
    if language is None or language.strip() == "":
        issues.append({
            "type": "Missing language attribute",
            "severity": "Medium",
            "element": "<html>",
            "description": "The <html> tag is missing a 'lang' attribute or it's empty.",
            "user_impact": "Users who rely on screen readers might not have the correct pronunciation or interpretation of the content.",
            "wcag": "3.1.1"
        })
    return issues

def check_empty_headings(soup):
    # Check for empty headings (WCAG 1.3.1)
    # Success Criterion 1.3.1: Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.
    
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    issues = []

    for heading in headings:
        if heading.get_text(strip=True):
            continue

        has_image_alt = False
        for img in heading.find_all('img'):
            if img.get('alt', '').strip():
                has_image_alt = True
                break
        if has_image_alt:
            continue
        if heading.get('aria-label', '').strip() or heading.get('aria-labelledby', '').strip():
            continue

        issues.append({
            "type": "Empty heading",
            "severity": "Low",
            "element": str(heading),
            "description": "A heading tag is present but has no text content.",
            "user_impact": "Users who rely on screen readers might have difficulty understanding the content hierarchy.",
            "wcag": "1.3.1"
        })
    return issues

def check_empty_buttons(soup):
    # Check for empty buttons (WCAG 4.1.2)
    # Success Criterion 4.1.2: For all user interface components (including but not limited to: form elements, links and components generated by scripts), the name and role can be programmatically determined; states, properties, and values that can be set by the user can be programmatically set; and notification of changes to these items is available to user agents, including assistive technologies.
    buttons = soup.find_all('button')
    issues = []

    for button in buttons:
        if button.get_text(strip=True):
            continue
        if button.get('aria-label', '').strip() or button.get('aria-labelledby', '').strip():
            continue
        
        issues.append({
            "type": "Empty button",
            "severity": "Medium",
            "element": str(button),
            "description": "A button is present but has no text content.",
            "user_impact": "Users who rely on screen readers might not know the purpose of the button.",
            "wcag": "4.1.2"
        })

    return issues


def analyze_page(soup):
    # Run all accessibility checks and return a list of issues found
    
    issues = []
    issues.extend(check_page_title(soup))
    issues.extend(check_images(soup))
    issues.extend(check_forms(soup))
    issues.extend(check_headings(soup))
    issues.extend(check_links(soup))
    issues.extend(check_language(soup))
    issues.extend(check_empty_headings(soup))
    issues.extend(check_empty_buttons(soup))
    return issues

def summarize_results(results):
    high = 0
    medium = 0
    low = 0

    for issue in results:
        if issue['severity'].lower() == "high":
            high += 1
        elif issue['severity'].lower() == "medium":
            medium += 1
        elif issue['severity'].lower() == "low":
            low += 1
   
    missing_page_title = 0
    missing_alt_text = 0
    missing_form_labels = 0
    empty_links = 0
    heading_structure_issues = 0
    missing_language_attribute = 0
    empty_headings = 0
    empty_buttons = 0

    for issue in results:
        if issue['type'] == "Missing page title":
            missing_page_title += 1
        elif issue['type'] == "Missing alt text":
            missing_alt_text += 1
        elif issue['type'] == "Form input without label":
            missing_form_labels += 1
        elif issue['type'] == "Empty link":
            empty_links += 1
        elif issue['type'] == "Empty heading":
            empty_headings += 1
        elif issue['type'] == "Incorrect heading structure":
            heading_structure_issues += 1
        elif issue['type'] == "Missing language attribute":
            missing_language_attribute += 1
        elif issue['type'] == "Empty button":
            empty_buttons += 1

    return {
        "high": high,
        "medium": medium,
        "low": low,
        "total": len(results),
        "missing_page_title": missing_page_title,
        "missing_alt_text": missing_alt_text,
        "missing_form_labels": missing_form_labels,
        "empty_links": empty_links,
        "heading_structure_issues": heading_structure_issues,
        "missing_language_attribute": missing_language_attribute,
        "empty_headings": empty_headings,
        "empty_buttons": empty_buttons
    }

def display_results(results):
    # Display all findings through the CLI
    summary = summarize_results(results)

    print("SUMMARY")
    print("----------------------------------------------")

    print("High Severity: " + str(summary["high"]))
    print("Medium Severity: " + str(summary["medium"]))
    print("Low Severity: " + str(summary["low"]))
    print("Total Issues: " + str(summary["total"]))
    print()

    print("ISSUES BY CATEGORY")
    print("----------------------------------------------")
    print("Missing Page Title: " + str(summary["missing_page_title"]))
    print("Missing Alt Text: " + str(summary["missing_alt_text"]))
    print("Missing Form Label: " + str(summary["missing_form_labels"]))
    print("Empty Link: " + str(summary["empty_links"]))
    print("Improper Heading Structure: " + str(summary["heading_structure_issues"]))
    print("Missing Language Attribute: " + str(summary["missing_language_attribute"]))
    print("Empty Headings: " + str(summary["empty_headings"]))
    print("Empty Buttons: " + str(summary["empty_buttons"]))
    print("==============================================")

    
    if len(results) == 0:
        print("No accessibility issues found.")
    else:
        print("DETAILED ISSUES")
        for issue in results:
            print("[" + str(issue['severity']).upper() + "] " + str(issue['type']))
            print("WCAG: " + str(issue['wcag']))
            print("Element: " + str(issue['element']))
            print("Description: " + str(issue['description']))
            print("User Impact: " + str(issue['user_impact']))
            print("---------------------------------")

def get_user_input():
    # Get the website URL from the user
    
    url = input("Enter the website URL: ")
    
    return url


# Testing
# html = get_webpage("https://beautiful-soup-4.readthedocs.io/en/latest/")
# soup = parse_html(html)


if __name__ == "__main__":
    # Run the accessibility checker
    url = get_user_input()
    html = get_webpage(url)
    print("==============================================")
    print("        ACCESSIBILITY ANALYSIS RESULTS")
    print("==============================================")
    print()
    print("Website: " + url)
    print()

    if html is None:
        print("Failed to analyze the website.")
        exit()
    else:
        soup = parse_html(html)

    analysis_results = analyze_page(soup)
    display_results(analysis_results)

    # Testing fast_a11y
    # fast_a11y_results = fast_a11y(html)
    # print(fast_a11y_results["violations"])