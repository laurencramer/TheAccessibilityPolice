# The Accessibility Police
# An Automated Website Accessibility Checker

# This program analyzes a website's HTML to identify common accessibility issues
# based on selected WCAG guidelines. It checks for issues like missing page titles, 
# missing language information, missing image alt text, forms without labels, unclear
# links, and problematic heading structures. The program explains each issue, its
# potential impact on users, and provides a recommended fix.
# Running this file will launch the Streamlit web app. 

# Bad websites to try (should go into ReadMe.md!) 
# https://www.fake-university.com/
# https://www.w3.org/WAI/demos/bad/before/home.html
# https://de.torontomu.ca/wa/lulu/
# https://projects.accesscomputing.uw.edu/au/before.html
# https://openassessittoolkit.github.io/accessible_u/before_u.html
# https://pandasaurusgames.com/


import streamlit as st
import accessibility_checker_CH2
import html as html_module


st.set_page_config(
    page_title="The Accessibility Police",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #F1F5F9;
}
/* Styling for the header/jumbron */
.jumbotron {
    background-color: #172554;
    padding: 2rem;
    border-radius: 0.5rem;
    margin-bottom: 2rem;
    }
.jumbotron-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0;
    color: #ffffff;
    }
.subtitle {
    font-size: 1.5rem;
    font-weight: 400;
    color: #ffffff;
    }

/* Styling for the URL input and issue count containers */
.st-key-url-container,
.st-key-issue-container {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 0.5rem;
    }

/* Styling for the analyze button */
.stButton > button {
    background-color: #2563EB;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #1D4ED8;
    color: #ffffff;
    border: none;
}

/* Styling for the Issues by Type header */
.filter-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #172554;
}

/* Styling for the issue cards */
.issue-heading {
    color: #172554;
    font-size: 1.3rem;
    font-weight: 700;
}

/* Styling for the severity labels */
.severity {
    font-size: 0.9rem;
    padding: 5px 10px;
    border-radius: 20px;
    background-color: #fff0f0;
    color: #d93636;
    font-weight: 700;
}
.severity.medium {
    background-color: #fff5e5;
    color: #b7791f;
}
.severity.low {
    background-color: #e8f7ef;
    color: #16834f;
}

/* Styling for the issue card icons */
.material-icons {
    font-family: 'Material Symbols Outlined';
    font-size: 40px;
    font-weight: normal;
    font-style: normal;
    line-height: 1;
}

/* Styling for the issue cards */
div[class*="st-key-issue-card-"] {
    background-color: white;
    border: 1px solid #dce2ed;
    border-left: 4px solid #ef4444;
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 15px;
}
div[class*="st-key-issue-card-medium-"] {
    border-left-color: #f59e0b;
}
div[class*="st-key-issue-card-low-"] {
    border-left-color: #22c55e;
}

/* Adjust the gap between the cards */
[data-testid="stVerticalBlock"] {
    gap: 0.7rem;
}

</style>
""", unsafe_allow_html=True
)

st.markdown("""
<div class="jumbotron">
    <div class="jumbotron-title">The Accessibility Police</div>
    <div class="subtitle">AN AUTOMATED WEBSITE ACCESSIBILITY CHECKER</div>
</div>
""", unsafe_allow_html=True)

# URL Input Container
with st.container(border=True, key="url-container"):
    st.markdown("Enter a website URL:")
    url = st.text_input("Website URL", placeholder="https://example.com", label_visibility="collapsed", key="url_input")
    analyze = st.button(
        ":material/search: Analyze Website",
        use_container_width=True
)

# Analyze the website when the button is clicked
if analyze:
    html = accessibility_checker_CH2.get_webpage(url)

    if html is None:
        st.error("Could not retrieve that website. It may use bot protection (e.g. Cloudflare) "
                    "that blocks automated requests, have a certificate problem, or the URL may be incorrect.")
        st.stop()

    soup = accessibility_checker_CH2.parse_html(html)
    results = accessibility_checker_CH2.analyze_page(soup)

    # Define the issue categories and their corresponding icons
    categories = [
        "Missing page title",
        "Missing alt text",
        "Form input without label",
        "Empty link",
        "Incorrect heading structure",
        "Missing language attribute",
        "Empty heading",
        "Empty button",
        "Missing table headers"
    ]   

    issue_icons = {
        "Missing page title": ":material/description:",
        "Missing alt text": ":material/image:",
        "Form input without label": ":material/label:",
        "Empty link": ":material/link:",
        "Incorrect heading structure": ":material/account_tree:",
        "Missing language attribute": ":material/translate:",
        "Empty heading": ":material/title:",
        "Empty button": ":material/radio_button_checked:",
        "Missing table headers": ":material/rule:"
    }

    # Count the number of issues for each category
    counts = {}
    for category in categories:
        count = 0
        for issue in results:
            if issue["type"] == category:
                count += 1
        counts[category] = count

    sidebar, main = st.columns([1, 4])

    # Display the issue by type counts in the sidebar
    with sidebar:
        with st.container(border=True, key="issue-container"):
            st.markdown(
                '<div class="filter-title">Issues by Type</div>',
                unsafe_allow_html=True
            )
            for category in categories:
                count = counts[category]
                st.markdown(f"""
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 10px;
                        font-size: 0.8rem;
                        gap: 8px;
                    ">
                        <span>{category}</span>
                        <span style="
                            background-color: #f1f5f9;
                            border-radius: 20px;
                            padding: 5px;
                            font-weight: 600;
                        ">{count}</span>
                    </div>
                """, unsafe_allow_html=True)
    
    # Display the detailed issues in the main area
    with main:
        if results:
            for i, issue in enumerate(results):
                severity = issue["severity"].lower()
                issue_type = issue["type"]
                description = issue["description"]
                element = html_module.escape(issue["element"])
                wcag = issue["wcag"]
                user_impact = issue["user_impact"]
                recommended_fix = issue["recommended_fix"]
                issue_icon = issue_icons[issue_type]

                # Used Copilot to generate the following code snippet (card_key) for creating a unique key for each issue card,
                # because I kept getting a Streamlit error about duplicate keys
                card_key = f"issue-card-{severity}-{i}"

                with st.container(key=card_key):
                    icon_column, heading_column, severity_column = st.columns([0.5, 9, 1])

                    with icon_column:
                        st.markdown(
                            f'<span class="material-icons">{issue_icon}</span>',
                            unsafe_allow_html=True
                        )
                    with heading_column:
                        st.markdown(
                            f'<span class="issue-heading">{issue_type}</span>',
                            unsafe_allow_html=True
                        )
                    with severity_column:
                        st.markdown(
                            f'<span class="severity {severity}">{severity.upper()}</span>',
                            unsafe_allow_html=True
                        )
                    st.write(description)
                    if issue.get("line"):
                        st.markdown(f"**Line:** {issue['line']}")
                    st.code(element, language="html")
                    st.markdown(f"**WCAG:** {wcag}")
                    st.markdown(f"**User Impact:** {user_impact}")
                    st.markdown(f"**Recommended Fix:** {recommended_fix}")
        else:
            st.info("No accessibility issues found.")

