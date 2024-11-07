import os
import csv
import unicodedata
from dotenv import load_dotenv
from linkedin_api import Linkedin

# Load environment variables from .env file
load_dotenv()

# Retrieve LinkedIn credentials from the environment variables
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

# Authenticate with your LinkedIn credentials
api = Linkedin(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)

# Function to normalize company names
def normalize_name(name):
    return unicodedata.normalize('NFC', name.strip().lower())

# Function to search employees by company using LinkedIn API
def search_employees_by_company(company_name):
    try:
        profiles = api.search_people(keywords=[company_name], include_private_profiles=True)
        return profiles
    except Exception as e:
        print(f"Error searching for employees at {company_name}: {e}")
        return []

# Function to check if a company has already been fetched
def has_company_been_fetched(company_name):
    normalized_name = normalize_name(company_name)
    try:
        with open('fetched_companies.txt', 'r', encoding='utf-8') as file:
            fetched_companies = set(normalize_name(line.strip()) for line in file)
        return normalized_name in fetched_companies
    except FileNotFoundError:
        return False

# Function to update the fetched companies list
def update_fetched_companies(company_name):
    normalized_name = normalize_name(company_name)
    with open('fetched_companies.txt', 'a', encoding='utf-8') as file:
        file.write(f"{normalized_name}\n")

# Function to fetch URNs for a company and write to a text file
def fetch_employees(company_name):
    if has_company_been_fetched(company_name):
        print(f"Company '{company_name}' has already been fetched. Skipping URN fetching.")
        return None

    urn_ids_file = f"{company_name.replace(' ', '_')}_employee_urn_ids.txt"
    profiles = search_employees_by_company(company_name)

    if profiles:
        with open(urn_ids_file, 'w', encoding='utf-8') as file:
            for idx, profile in enumerate(profiles, start=1):
                urn_id = profile.get('urn_id')
                if urn_id:
                    print(f"Profile {idx}: {urn_id}")
                    file.write(f"{urn_id}\n")
        # Update the fetched companies list
        update_fetched_companies(company_name)
        return urn_ids_file
    else:
        print(f"No profiles found for {company_name}")
        return None

# Function to fetch LinkedIn profile data based on URN
def get_profile_data_urn(urn_id):
    try:
        profile = api.get_profile(urn_id)
        data = {
            'name': profile.get('firstName', '') + ' ' + profile.get('lastName', ''),
            'occupation': profile.get('headline', ''),
            'company': profile['experience'][0]['companyName'] if profile.get('experience') else None,
            'certifications': ', '.join([cert['name'] for cert in profile.get('certifications', [])]),
            'skills': ', '.join([skill['name'] for skill in profile.get('skills', [])]),
            'post_titles': ', '.join([post['title'] for post in profile.get('publications', [])]),
            'industry': profile.get('industryName', 'N/A'),
            'location': profile.get('locationName', 'N/A'),
            'languages': ', '.join([lang['name'] for lang in profile.get('languages', [])]),
            'experience': ', '.join([f"{exp['title']} at {exp['companyName']}" for exp in profile.get('experience', [])]),
        }
        return data
    except Exception as e:
        print(f"Error fetching profile data for {urn_id}: {e}")
        return None

# Function to fetch and write profiles to separate CSV files
def write_profiles_to_csv(company_name, urls_file):
    # Check if the company has already been fetched (for URNs only)
    if not has_company_been_fetched(company_name):
        urn_ids_file = fetch_employees(company_name)

    urn_ids_file = f"{company_name.replace(' ', '_')}_employee_urn_ids.txt"
    employee_csv_file = f"{company_name.replace(' ', '_')}_linkedin_profiles.csv"  # Employee CSV name
    contestant_csv_file = f"{company_name.replace(' ', '_')}_contestant_linkedin_profiles.csv"  # Contestant CSV name

    # Read URN IDs
    urn_ids = []
    if os.path.isfile(urn_ids_file):
        with open(urn_ids_file, 'r', encoding='utf-8') as file:
            urn_ids = [line.strip() for line in file if line.strip()]

    # Read URLs
    with open(urls_file, 'r', encoding='utf-8') as file:
        profile_urls = [line.strip() for line in file if line.strip()]

    csv_columns = ['Name', 'Occupation', 'Company', 'Certifications', 'Skills', 'Post Titles', 'Industry', 'Location', 'Languages', 'Experience']
    
    # Write employee data
    write_csv_file(employee_csv_file, csv_columns, urn_ids)
    
    # Write contestant data (always run even if the company has been fetched)
    write_csv_file(contestant_csv_file, csv_columns, profile_urls, use_urls=True)

def write_csv_file(csv_file, csv_columns, ids, use_urls=False):
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=csv_columns)
        if not file_exists:
            writer.writeheader()

        unique_profiles = set()

        # Fetch data for URN IDs or URLs
        for identifier in ids:
            if use_urls:
                profile_id = identifier.split('/')[-2]  # Extract ID from URL
            else:
                profile_id = identifier
            
            if profile_id not in unique_profiles:
                unique_profiles.add(profile_id)
                profile_data = get_profile_data_urn(profile_id)
                if profile_data:
                    writer.writerow(profile_data)
                    print(f"Data fetched for: {profile_data['name']}")

    print(f"Data has been successfully written to {csv_file}")

company_name = "Huawei Cloud Türkiye"
urn_ids_file = fetch_employees(company_name)
if urn_ids_file:
    write_profiles_to_csv(company_name, 'profile_urls.txt')
