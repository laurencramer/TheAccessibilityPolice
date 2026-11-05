import streamlit as st
import accessibility_checker

st.markdown("""
<style>
.stApp {
    background-color: #F1F5F9;
}
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

.st-key-url-container {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 0.5rem;
    }

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


st.markdown("""
<div class="jumbotron">
    <div class="jumbotron-title">The Accessibility Police</div>
    <div class="subtitle">AN AUTOMATED WEBSITE ACCESSIBILITY CHECKER</div>
</div>
""", unsafe_allow_html=True)



with st.container(border=True, key="url-container"):
    st.markdown("Enter a website URL:")
    url = st.text_input("Website URL", placeholder="https://example.com", label_visibility="collapsed", key="url_input")


    analyze = st.button(
        ":material/search: Analyze Website",
        use_container_width=True
)

if analyze:
    html = accessibility_checker.get_webpage(url)
    # CH
    if html is None:
        st.error("Could not retrieve that website. It may use bot protection (e.g. Cloudflare) "
                 "that blocks automated requests, have a certificate problem, or the URL may be incorrect.")
        st.stop()
    # CH
    soup = accessibility_checker.parse_html(html)
    results = accessibility_checker.analyze_page(soup)

    if results:
        st.divider()
        st.subheader("ISSUES SUMMARY")

        summary = accessibility_checker.summarize_results(results)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.error("High Severity")
            st.metric("",summary['high'])
        with col2:
            st.warning("Medium Severity")
            st.metric("",summary['medium'])
        with col3:
            st.success("Low Severity")
            st.metric("", summary['low'])
        with col4:
            st.info("Total Issues")
            st.metric("", summary['total'])

        st.divider()

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

        st.divider()

        st.subheader("DETAILED ISSUES")

        for issue in results:
            with st.container(border=True, gap="small"):
                col1, col2 = st.columns([9, 1])

                with col1:
                    st.markdown("**" + issue['type'] + "**")
                with col2:
                    if issue['severity'].lower() == "high":
                        st.badge(issue['severity'].upper(), color="red")
                    elif issue['severity'].lower() == "medium":
                        st.badge(issue['severity'].upper(), color="yellow")
                    elif issue['severity'].lower() == "low":
                        st.badge(issue['severity'].upper(), color="green")

                st.caption("WCAG: " + issue['wcag'])

                st.markdown(
                    """
                    <div style="
                        border-top: 1px solid #d1d5db;
                        margin-top: 2px;
                        margin-bottom: 10px;
                        width: 100%;
                    "></div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("**Description:**")
                st.write(issue['description'])

                st.markdown("**Element:**")
                st.code(issue['element'], language='html')

                st.markdown("**User Impact:**")
                st.write(issue['user_impact'])
        
    else:
        st.write("No accessibility issues found.")

