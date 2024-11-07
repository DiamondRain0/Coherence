import os
import csv
from dotenv import load_dotenv
from linkedin_api import Linkedin
import pandas as pd
import random

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Create a FastAPI instance
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Pydantic model to define the structure of data for request bodies
class Item(BaseModel):
    url: str

@app.post("/url")
async def create_item(item: Item):
    skills, certificates = find_needed_skills(item.url)
    return {"skills": skills, "certificates": certificates}



#CSV already created for the first stage


def get_public_identifier(url):
    try:
        profile_id = url.split('/')[-2]  # Adjusting to ensure public identifier is correctly parsed
        return profile_id
    except IndexError:
        print(f"Invalid URL format: {url}")
        return None

# Function to fetch and extract relevant data from a profile
def get_profile_data_url( profile_id , api ):
    try:
        profile = api.get_profile(profile_id)
        #print(f"Fetched profile for: {profile_id}")  # Debugging statement

        # Extract relevant fields
        data = {
            'name': profile.get('firstName', '') + ' ' + profile.get('lastName', ''),
            'occupation': profile.get('headline', ''),
            'company': profile['experience'][0]['companyName'] if profile.get('experience') else None,
            'certifications': ', '.join([cert['name'] for cert in profile.get('certifications', [])]),
            'skills': ', '.join([skill['name'] for skill in profile.get('skills', [])]),
            'post_titles': ', '.join([post['title'] for post in profile.get('publications', [])]),
            'industry': profile.get('industryName', 'N/A'),  # Adding industry
            'location': profile.get('locationName', 'N/A'),  # Adding location
            'languages': ', '.join([lang['name'] for lang in profile.get('languages', [])]),  # Adding languages
            'experience': ', '.join([f"{exp['title']} at {exp['companyName']}" for exp in profile.get('experience', [])]),  # Adding experience
        }
        return data
    except Exception as e:
        print(f"Error fetching profile data for {profile_id}: {e}")
        return None

# Function to read profile URLs from a text file
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
    return urls

def find_needed_skills(url):

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve LinkedIn credentials from the environment variables
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')



    api = Linkedin(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)

    # File paths

    csv_file = 'candidate.csv'

    # Read profile URLs from the text file

    #url = input("enter your linkedin url: ")


    # Prepare CSV file
    csv_columns = [
        'Name', 'Occupation', 'Company', 'Certifications', 'Skills', 'Post Titles', 
        'Industry', 'Location', 'Languages', 'Experience'
    ]

    # Check if the CSV file already exists
    file_exists = os.path.isfile(csv_file)

    # Fetch data and write to CSV
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=csv_columns)
        
        # Write the header row only if the file is new
        if not file_exists:
            writer.writeheader()
        
        # Iterate over profile URLs and fetch data for each
        unique_profiles = set()  # To avoid duplicates
        profile_id = get_public_identifier(url)
            
        if profile_id and profile_id not in unique_profiles:  # Check for uniqueness and valid profile_id
            unique_profiles.add(profile_id)
            profile_data = get_profile_data_url(profile_id, api)
                
            if profile_data:
                    # Write profile data to CSV
                writer.writerow({
                    'Name': profile_data['name'],
                    'Occupation': profile_data['occupation'],
                    'Company': profile_data['company'],
                    'Certifications': profile_data['certifications'],
                    'Skills': profile_data['skills'],
                    'Post Titles': profile_data['post_titles'],
                    'Industry': profile_data['industry'],
                    'Location': profile_data['location'],
                    'Languages': profile_data['languages'],
                    'Experience': profile_data['experience']
                })
                #print(f"Data fetched for: {profile_data['name']}")  # Debugging output
            else:
                print(f"Failed to retrieve data for: {profile_id}")
        else:
            print(f"Duplicate or invalid profile ID skipped: {profile_id}")

    print(f"Data has been successfully written to {csv_file}")



    # talent recommentation




    # Function to read user data from a text file
    def read_user_data(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the first line and split by commas
            file.readline()
            line = file.readline().strip()
            # Split the line into parts
            parts = line.split(',')
            
            # Create a dictionary with the user data
            user_data = {
                'Name': parts[0],
                'Occupation': parts[1],
                'Company': parts[2],
                'Certifications': parts[3].strip('"'),  # Remove quotes
                'Skills': parts[4].strip('"'),  # Remove quotes
            }
            return user_data

    # Read user data from the text file
    user_data = read_user_data('candidate.csv')

    # Convert the user data into a DataFrame
    user_df = pd.DataFrame([user_data])

    # Read the skills and certifications count CSV files
    skills_count = pd.read_csv('talents/skills_count.csv')  # Skill, Count format
    certifications_count = pd.read_csv('talents/certifications_count.csv')  # Certification, Count format

    # Extract skills and certifications from the user data
    user_skills = set(user_df['Skills'].str.split(',').explode().str.strip())
    user_certifications = set(user_df['Certifications'].str.split(',').explode().str.strip())

    # Extract skills and certifications data from the CSVs
    skills_df = skills_count[['Skill', 'Count']].dropna()  # Remove rows with missing skills
    certifications_df = certifications_count[['Certification', 'Count']].dropna()  # Remove rows with missing certifications

    # Filter out the user's skills and certifications
    missing_skills_df = skills_df[~skills_df['Skill'].isin(user_skills)].sort_values(by='Count', ascending=False)  # Skills user doesn't have
    missing_certifications_df = certifications_df[~certifications_df['Certification'].isin(user_certifications)].sort_values(by='Count', ascending=False)  # Certifications user doesn't have

    top_10_missing_skills = missing_skills_df['Skill'].head(10).tolist()
    top_10_missing_certifications = missing_certifications_df['Certification'].head(10).tolist()

    # Randomly select 5 from the top 10
    recommended_skills = random.sample(top_10_missing_skills, 5)
    recommended_certifications = random.sample(top_10_missing_certifications, 5)

    # Print the recommended skills and certifications
    print("Recommended Skills:", recommended_skills)
    print("Recommended Certifications:", recommended_certifications)
    return recommended_skills, recommended_certifications


