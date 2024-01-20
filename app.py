import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

from dotenv import dotenv_values

config = dotenv_values(".env")

#get api key from config

API_KEY = config['API_KEY']

if not API_KEY:
    API_KEY = st.secrets['API_KEY']

LIMIT = 30  # No of jobs to fetch, can remove ?limit from URL to get all jobs

def crackeddevs(page):
    url = f'https://api.crackeddevs.com/api/get-jobs?limit={LIMIT}&page={page}'
    headers = {'api-key': API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Error: {response.status_code}")
        return None

# Streamlit UI
#aling image in center
st.set_page_config(page_title='Remote Co.', page_icon = './logo.png', layout = 'wide', initial_sidebar_state = 'auto')

st.sidebar.image('./logo.png', width=50)
st.sidebar.title('Remote Co.')
st.sidebar.write('Remote Co. is a job board for remote jobs in the tech industry.')
page_selection = st.sidebar.selectbox("Select Page", ["Job Viewer","Resources", "Demanding Roles", "Applications and Roles", "Technologies in Demand"])
def open_url_in_browser(url):
    import webbrowser
    webbrowser.open(url)

st.empty()

all_data = []

@st.cache_data
def fetch_data():
    for i in range(1,11):
        data = crackeddevs(i)
        if data:
            all_data.extend(data)
    return all_data

if page_selection == "Job Viewer":
    # Sidebar
    st.sidebar.title('Filter Jobs')
    all_data = crackeddevs(1)  # Assuming all data is fetched on page 1, adjust if needed

    st.title('Listed Jobs')

    df = pd.DataFrame(all_data)
    unique_locations = df['location_iso'].unique()

    # Create a dictionary for the location filter options
    location_options = {location: location for location in unique_locations}
    location_options.pop(None, None) 
    location_options.pop('', None)

    # Prepopulate the location filter with options
    # location_filter = st.sidebar.selectbox('Location Filter', [""] + list(location_options.keys()))
    salary_filter = st.sidebar.slider('Salary Range (USD)', 0, 150000, (0, 150000))

    # Pagination
    page = st.sidebar.number_input('Page', value=1, min_value=1)
    # next_page = st.sidebar.button('Next Page')

    # Fetch data
    with st.spinner('Loading data...'):
        data = crackeddevs(page)

    if data:
        for job in data:
            try:
                if (salary_filter[0] <= job.get('min_salary_usd', 0) <= salary_filter[1] or salary_filter[0] <= job.get('max_salary_usd', 0) <= salary_filter[1]):

                    # Job Card
                    try:
                        st.image(job['image_url'], caption=job['company'], width=100 if job['image_url'] else None)
                    except:
                        pass
                    st.markdown(f'<h3 style="color: #FFD700;">Role: {job["title"]}</h3>', unsafe_allow_html=True)
                    st.write(f"**Company:** {job['company']}")
                    st.write(f"**Salary Range:** ${job['max_salary_usd']} - ${job['min_salary_usd']}")
                    st.write(f"**Description:** {job['description']}")

                    # Additional Details
                    st.write(f"**Job URL:** [{job['title']}]({job['url']})")
                    created_at = datetime.fromisoformat(job['created_at'])
                    st.write(f"**Created At:** {created_at.strftime('%d %B %Y')}")
                    st.write(f"**Applications:** {job['applications']}")
                    st.write(f"**Views:** {job['views']}")

                    # Apply Button
                    st.button(f'Apply', key=f'apply_button_{job["id"]}', on_click=lambda url=job['url']: open_url_in_browser(url))

                    st.markdown("---")
            except Exception as e:
                pass

        # # Pagination logic
        # if next_page:
        #     st.sidebar.number_input('Page', value=page + 1, min_value=1, key='next_page')



elif page_selection == "Demanding Roles":
    st.title('Demanding Roles in the Market')
    
    # Fetch all data
    all_data = fetch_data()

    with st.spinner('Loading data...'):
        time.sleep(1)
    
    #in left sidebar show total number of jobs
    st.sidebar.title('Total Jobs')
    st.sidebar.write(len(all_data))


    # Create a DataFrame
    try:
        df = pd.DataFrame(all_data)
        roles = [
            "Software Engineer",
            "Software Developer",
            "Frontend Developer",
            "Backend Developer",
            "Fullstack Developer",
            "DevOps Engineer",
            "Data Scientist",
            "Data Engineer",
            "Machine Learning Engineer",
            "Product Manager",
            "Project Manager",
            "Business Analyst",
            "QA Engineer",
            "QA Analyst",
            "QA Tester",
            "QA Automation Engineer",
            "QA Automation Analyst",
            "QA Automation Tester",
            "Hackathon Organizer/Operator",
            "Cryptography Engineer",
            "Blockchain Engineer",
            "Blockchain Developer",
        ]

        # Preprocess the roles before counting
        df['role'] = df['title'].str.lower().str.replace(r'[^a-zA-Z0-9\s]', '')

        # Count the occurrences of each role
        role_counts = df['role'].value_counts()

        st.markdown("---")
        st.subheader('Most Demanding Roles')
        for idx, (technology, count) in enumerate(role_counts.head(3).items(), start=1):
            st.markdown(f"<font color='green'>{idx}. {technology.capitalize()}</font>", unsafe_allow_html=True)



        # Combine counts for roles in the specified array
        for role in roles:
            matching_roles = [r for r in role_counts.index if role.lower() in r]
            if matching_roles:
                combined_count = sum(role_counts[matching_roles])
                role_counts = role_counts.drop(matching_roles, errors='ignore')
                role_counts[role] = combined_count

        # Plotting the graph
        #filet if role_counts > 2
        role_counts = role_counts[role_counts > 2]

        st.markdown("---")
        st.subheader('Roles Distribution')
        st.bar_chart(role_counts)

        # Display the DataFrame
        st.subheader('Job Data')
        #remove id column from dataframe
        df = df.drop(columns=['id'])
        st.dataframe(df)

    except Exception as e:
        pass

elif page_selection == "Applications and Roles":
    st.title('Applications and Roles Distribution')

    # Fetch all data
    all_data = fetch_data()


    with st.spinner('Loading data...'):
        time.sleep(1)

    # Create a DataFrame
    try:
        df = pd.DataFrame(all_data)
        df = df.drop(columns=['id'])

        # Sidebar
        st.sidebar.title('Filter Applications')
        min_applications = st.sidebar.number_input('Minimum Applications', value=0)
        max_applications = st.sidebar.number_input('Maximum Applications', value=100, min_value=min_applications)

        # Filter data based on applications
        filtered_data = df[(df['applications'] >= min_applications) & (df['applications'] <= max_applications)]

        # Number of Applications
        st.markdown(f'<p style="background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;">Total Applications: {filtered_data["applications"].sum()}</p>', unsafe_allow_html=True)
        # Distribution of Roles based on Applications
        roles_applications_counts = filtered_data['title'].value_counts()

        # Plotting the graph
        st.bar_chart(roles_applications_counts)

        # Display the DataFrame
        st.subheader('Job Data')
        st.dataframe(filtered_data)

    except Exception as e:
        pass

elif page_selection == "Technologies in Demand":
    # Fetch all data
    
    all_data = fetch_data()

    with st.spinner('Loading data...'):
        time.sleep(1)

    # Create a DataFrame
    try:
        df = pd.DataFrame(all_data)

        # Sidebar
        # st.sidebar.title('Filter Technologies')
        # min_technologies = st.sidebar.number_input('Minimum Technologies Mentioned', value=0)
        min_technologies = 1

        # Extract technologies from the job descriptions
        # df['technologies'] = df['technologies'].str.extractall(r'([a-zA-Z0-9-]+)').groupby(level=0)[0].unique()

        # Count the occurrences of each technology
        technologies_counts = df['technologies'].explode().value_counts()

        st.markdown("### Most Demanding Technologies:", unsafe_allow_html=True)

        for idx, (technology, count) in enumerate(technologies_counts.head(3).items(), start=1):
            st.markdown(f"<font color='green'>{idx}. {technology.capitalize()}</font>", unsafe_allow_html=True)

        st.markdown("---")

        # Filter technologies based on the minimum count
        filtered_technologies = technologies_counts[technologies_counts >= min_technologies]

        # Plotting the graph
        st.header('Technologies Distribution')
        st.bar_chart(filtered_technologies)

        # st.subheader('Raw List')
        # st.dataframe(filtered_technologies, height=1000)
        #write all technologies in badge format
    except Exception as e:
        pass

elif page_selection == "Resources":

    try:
        st.title('Resources')
        st.markdown("---")

        # Data for the table
        resources_data = {
            "Job Portals": [
                {"Name": "LinkedIn", "Link": "https://www.linkedin.com/jobs/", "Description": "Professional networking and job portal."},
                {"Name": "Indeed", "Link": "https://www.indeed.com/", "Description": "A comprehensive job search engine."},
                {"Name": "Glassdoor", "Link": "https://www.glassdoor.com/index.htm", "Description": "Company reviews and job listings."},
                {"Name": "Monster", "Link": "https://www.monster.com/", "Description": "Global employment website."},
                {"Name": "Stackoverflow", "Link": "https://stackoverflow.com/jobs", "Description": "Job board for programmers."},
                {"Name": "RemoteOK", "Link": "https://remoteok.io/", "Description": "Remote job aggregator."},
                {"Name": "Remote.co", "Link": "https://remote.co/remote-jobs/", "Description": "Remote job listings and resources."},
                {"Name": "We Work Remotely", "Link": "https://weworkremotely.com/", "Description": "Remote job board."},
                {"Name": "AngelList", "Link": "https://angel.co/", "Description": "Platform for startups to hire talent."},
                {"Name": "Hired", "Link": "https://hired.com/", "Description": "Job search for tech talent."},
                {"Name": "Triplebyte", "Link": "https://triplebyte.com/", "Description": "Technical recruiting platform."},
                {"Name": "Dice", "Link": "https://www.dice.com/", "Description": "Tech job search and career hub."},
                {"Name": "Landing.jobs", "Link": "https://landing.jobs/", "Description": "Job board for tech professionals."},
                {"Name": "RemoteLeaf", "Link": "https://remoteleaf.com/", "Description": "Curated list of remote jobs in tech."},
                {"Name": "Remote.com", "Link": "https://remote.com/", "Description": "Remote job platform."},
                {"Name": "Remote Circle", "Link": "https://remotecircle.com/", "Description": "Community-driven remote job board."},
            ],
            "Freelancing": [
                {"Name": "Upwork", "Link": "https://www.upwork.com/", "Description": "Freelance platform for various skills."},
                {"Name": "Freelancer", "Link": "https://www.freelancer.com/", "Description": "Freelance jobs and contests."},
                {"Name": "Fiverr", "Link": "https://www.fiverr.com/", "Description": "Freelance services marketplace."},
                {"Name": "Toptal", "Link": "https://www.toptal.com/", "Description": "Freelance talent marketplace."},
                {"Name": "Guru", "Link": "https://www.guru.com/", "Description": "Freelance marketplace for professionals."},
            ],
            "Remote Companies": [
                {"Name": "GitLab", "Link": "https://about.gitlab.com/jobs/", "Description": "Web-based Git repository manager."},
                {"Name": "Zapier", "Link": "https://zapier.com/jobs/", "Description": "Automation for busy people."},
                {"Name": "Automattic", "Link": "https://automattic.com/work-with-us/", "Description": "Web development company known for WordPress."},
                {"Name": "InVision", "Link": "https://www.invisionapp.com/company#jobs", "Description": "Digital product design platform."},
                {"Name": "Hotjar", "Link": "https://careers.hotjar.com/", "Description": "Behavior analytics and user feedback platform."},
                {"Name": "Toggl", "Link": "https://toggl.com/jobs/", "Description": "Time tracking and productivity tool."},
                {"Name": "Doist", "Link": "https://doist.com/jobs/", "Description": "Creators of Todoist and Twist."},
                {"Name": "Aha!", "Link": "https://www.aha.io/company/careers/current-openings", "Description": "Product roadmap software company."},
                {"Name": "Close", "Link": "https://jobs.lever.co/close.io/", "Description": "Inside sales CRM."},
                {"Name": "TaxJar", "Link": "https://www.taxjar.com/jobs/", "Description": "Sales tax automation software."},
                {"Name": "DuckDuckGo", "Link": "https://duckduckgo.com/hiring/", "Description": "Privacy-focused search engine."},
                {"Name": "Clevertech", "Link": "https://www.clevertech.biz/careers", "Description": "Remote-first technology consultancy."},
                {"Name": "Crossover", "Link": "https://www.crossover.com/", "Description": "Remote work staffing platform."},
                {"Name": "Scrapinghub", "Link": "https://scrapinghub.com/jobs", "Description": "Data extraction platform."},
                {"Name": "X-Team", "Link": "https://x-team.com/join/", "Description": "Community of developers working remotely."},
                {"Name": "Dell", "Link": "https://jobs.dell.com/", "Description": "Computer technology company."},
                {"Name": "GitBook", "Link": "https://jobs.gitbook.com/", "Description": "Documentation platform."},
                {"Name": "Hubstaff", "Link": "https://hubstaff.com/jobs", "Description": "Time tracking and productivity software."},
                {"Name": "Inflow", "Link": "https://www.goinflow.com/careers/", "Description": "E-commerce digital marketing agency."},
                {"Name": "Knack", "Link": "https://www.knack.com/careers", "Description": "No-code platform for building online databases."},
            ],
            "GitHub Repositories": [
                {"Name": "Awesome Remote Job", "Link": "https://github.com/lukasz-madon/awesome-remote-job", "Description": "Curated list of awesome remote job opportunities."},
                {"Name": "Awesome Remote Freelance", "Link": "https://github.com/kaizensoze/awesome-freelance-jobs", "Description": "Curated list of freelancing platforms."},
                {"Name": "Awesome Remote Companies", "Link": "https://github.com/remoteintech/remote-jobs", "Description": "Curated list of companies offering remote jobs."},
                {"Name": "Awesome Remote Work", "Link": "https://github.com/hugo53/awesome-remote-work", "Description": "Curated list of resources for remote workers."},
            ],
            "Blogs": [
                {"Name": "Remote.co", "Link": "https://remote.co/", "Description": "Remote work tips, news, and resources."},
                {"Name": "Remote OK", "Link": "https://remoteok.io/", "Description": "Remote job board and community."},
                {"Name": "Remote Leaf", "Link": "https://remoteleaf.com/", "Description": "Curated list of remote job opportunities."},
                {"Name": "Remote.com", "Link": "https://remote.com/", "Description": "Remote work insights and job board."},
            ],
            "Podcasts": [
                {"Name": "Remote Work Life", "Link": "", "Description": "Podcast about the remote work lifestyle."},
                {"Name": "The Remote Show", "Link": "", "Description": "Podcast featuring interviews with remote companies."},
                {"Name": "The Remote Work Podcast", "Link": "", "Description": "Podcast discussing remote work topics."},
                {"Name": "The Remote Work Channel", "Link": "", "Description": "Podcast covering various aspects of remote work."},
                {"Name": "The Remote Work Podcast", "Link": "", "Description": "Podcast exploring remote work trends and challenges."},
            ],
            "Communities": [
                {"Name": "Remote Work Hub", "Link": "", "Description": "Online community for remote workers."},
                {"Name": "Remote Work Subreddit", "Link": "", "Description": "Subreddit dedicated to remote work discussions."},
                {"Name": "Remote Work Facebook Group", "Link": "", "Description": "Facebook group for remote work enthusiasts."},
                {"Name": "Remote Work Slack Group", "Link": "", "Description": "Slack group for remote work professionals."},
                {"Name": "Remote Work LinkedIn Group", "Link": "", "Description": "LinkedIn group for remote work networking."},
                {"Name": "Remote Work Meetup Group", "Link": "", "Description": "Local and virtual meetups for remote workers."},
            ],
            "Books": [
                {"Name": "Remote", "Link": "", "Description": "Book by Jason Fried and David Heinemeier Hansson on remote work."},
                {"Name": "Remote Work", "Link": "", "Description": "Book by Chris Guillebeau exploring the world of remote work."},
                {"Name": "Remote Work Revolution", "Link": "", "Description": "Book by Tsedal Neeley on the future of remote work."},
                {"Name": "The Year Without Pants", "Link": "", "Description": "Book by Scott Berkun about working at WordPress.com."},
                {"Name": "The Ultimate Guide to Remote Work", "Link": "", "Description": "Book by Zapier on successful remote work practices."},
            ],
            "Courses": [
                {"Name": "Remote Work Mastery", "Link": "", "Description": "Online course for mastering remote work skills."},
                {"Name": "Remote Work School", "Link": "", "Description": "Educational platform for remote work courses."},
                {"Name": "Remote Work Academy", "Link": "", "Description": "Academy offering courses for remote work professionals."},
                {"Name": "Remote Work School", "Link": "", "Description": "School providing resources and courses for remote work."},
            ],
        }

        tabs = list(resources_data.keys())
        selected_tab = st.radio("Select a category", tabs)

        # Display the table for the selected category
        df = pd.DataFrame(resources_data[selected_tab])
        #add a button to open the link in a new tab
        
        st.dataframe(df)

        st.markdown("---")

    except:
        pass



