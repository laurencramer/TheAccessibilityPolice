import streamlit as st
import accessibility_checker

st.markdown("""
<style>
[data-testid="column"] {
    text-align: center;
    }
[data-testid="stMetric"] {
    text-align: center;
    }
    
[data-testid="stAlert"] {
    text-align: center;
    margin-bottom: -20px;
    }

</style>
""", unsafe_allow_html=True
)


st.title("The Accessibility Police")
st.write("An Automated Website Accessibility Checker")

url = st.text_input("Enter a website URL: ")

if st.button("Analyze Website"):
    html = accessibility_checker.get_webpage(url)
    soup = accessibility_checker.parse_html(html)
    results = accessibility_checker.analyze_page(soup)

    if results:
        st.subheader("ISSUES SUMMARY")

        summary = accessibility_checker.summarize_results(results)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.error("High Severity")
            st.metric("High Severity", summary['high'], label_visibility="collapsed")
        with col2:
            st.warning("Medium Severity")
            st.metric("Medium Severity", summary['medium'], label_visibility="collapsed")
        with col3:
            st.success("Low Severity")
            st.metric("Low Severity", summary['low'], label_visibility="collapsed")
        with col4:
            st.info("Total Issues")
            st.metric("Total Issues", summary['total'], label_visibility="collapsed")

        st.subheader("ISSUES BY CATEGORY")

        categories = [
            ("Missing Page Title", summary['missing_page_title'], "description"),
            ("Missing Alt Text", summary['missing_alt_text'], "image"),
            ("Missing Form Label", summary['missing_form_labels'], "label"),
            ("Empty Link", summary['empty_links'], "link_2"),
            ("Improper Heading Structure", summary['heading_structure_issues'], "format_list_numbered"),
            ("Missing Language Attribute", summary['missing_language_attribute'], "translate"),
            ("Empty Headings", summary['empty_headings'], "format_h1"),
            ("Empty Buttons", summary['empty_buttons'], "left_click"),
        ]

        for start in range(0, len(categories), 2):
            cols = st.columns(2)

            for col, (category_name, count, icon) in zip(cols, categories[start:start + 2]):
                with col:
                    with st.container(border=True):
                        st.markdown(":material/" + icon + ":")
                        st.metric(category_name, count)

        st.subheader("DETAILED ISSUES")

        for issue in results:
            if issue['severity'].lower() == "high":
                st.badge(issue['severity'].upper(), color="red")
            elif issue['severity'].lower() == "medium":
                st.badge(issue['severity'].upper(), color="yellow")
            elif issue['severity'].lower() == "low":
                st.badge(issue['severity'].upper(), color="green")
            st.write(issue['type'])
            st.write("WCAG: " + issue['wcag'])
            st.write("Description: " + issue['description'])
            st.write("Element: " + issue['element'])
            st.write("User Impact: " + issue['user_impact'])
            st.divider()

        
    else:
        st.write("No accessibility issues found.")

