
# 📊 UYUM -Shaolin Keşişleri-

Empowering Talent Acquisition with Automation and Innovation
This project supports SDG 8: Decent Work and Economic Growth by providing an automated solution for efficient recruitment, helping companies and HR teams match talent with the right skills, leading to better employment opportunities and economic development.

Automate and streamline LinkedIn profile data fetching, processing, and analysis using FastAPI. This tool helps extract, store, and analyze profiles to assist in talent acquisition, skill assessments, and profile matching.

---

## 📑 Table of Contents
- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Docker Setup](#docker-setup)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
  - [Fetching Company Data](#fetching-company-data)
  - [Recommending Skills & Certifications](#recommending-skills--certifications)
  - [Ranking Contestants](#ranking-contestants)
- [Acknowledgments](#acknowledgments)

---

## 📝 Introduction

This project provides an automated approach to handle LinkedIn profile data, ideal for HR teams and recruitment agencies. By leveraging the LinkedIn API and sentence-transformer models, UYUM enhances recruitment by enabling:

1. Collecting employee profile data for specific companies.
2. Matching and ranking candidates based on their similarity to company profiles.
3. Recommending missing skills and certifications to enhance candidate profiles.

Aligned with SDG 8, this tool seeks to foster decent work and economic growth by simplifying the process of identifying the right talent, improving skills matching, and streamlining hiring processes.

## 🗂 Project Structure

Here’s a breakdown of the main files in the project:

- **prepare_company_data.py**: Collects LinkedIn data for a specific company. Searches for employee profiles, fetches URNs, and saves details to CSV.
- **user_backend.py**: FastAPI backend that provides an API endpoint to fetch missing skills and certifications for LinkedIn profiles.
- **hr_backend.py**: FastAPI backend that processes profile CSV files for employees and contestants, then calculates similarity scores and ranks contestants based on weighted averages.
- **Dockerfile**: Defines the Docker image to containerize the application for consistent deployment.
- **requirements.txt**: Lists all the required Python packages for the project.

---

## ✨ Features

- **LinkedIn Profile Fetching**: Retrieve and save profile data, including name, skills, certifications, and experiences, for employees of a specified company.
- **Skill & Certification Recommendations**: Analyze profiles to suggest additional skills and certifications a candidate might need.
- **Contestant Ranking**: Rank contestants based on their similarity to company profiles using semantic embeddings.
- **CSV Data Export**: Export profile data and ranking results to CSV for easy review and reporting.

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.7+
- Libraries: FastAPI, dotenv, pandas, sentence-transformers, LinkedIn API library (e.g., `linkedin-api`)

### Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-repo/Uyum.git
cd Uyum
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

1. Create a `.env` file in the project root to store LinkedIn API credentials.
2. Set the following variables:
    ```plaintext
    LINKEDIN_EMAIL=your_email@example.com
    LINKEDIN_PASSWORD=your_password
    ```

---

## 🐳 Docker Setup

To make deployment easier, you can containerize the project with Docker.

1. **Build the Docker image:**
   ```bash
   docker build -t Uyum .
   ```

2. **Run the Docker container:**
   ```bash
   docker run -p 8000:8000 Uyum
   ```

> **Note:** The Dockerfile uses Python 3.9-slim as the base image and installs dependencies from `requirements.txt`. It runs the specified Python script when the container starts.

---

## 📡 API Endpoints

### User Backend (`user_backend.py`)
| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `POST` | `/url` | Accepts a LinkedIn profile URL and returns missing skills and certifications. |

#### Example Request
```json
POST /url
{
  "url": "https://www.linkedin.com/in/sample-profile"
}
```

### HR Backend (`hr_backend.py`)
| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `POST` | `/process-csv/` | Accepts two CSV files (employee profiles and contestant profiles), calculates similarity scores, and returns ranked CSV of contestants. |

#### Example Request
Upload two files in form-data:
- `file1`: Employee profiles CSV
- `file2`: Contestant profiles CSV

---

## 🚀 Usage

### 1️⃣ Fetching Company Data
Run `prepare_company_data.py` to collect LinkedIn profiles for employees. Results are saved in CSV format.
```bash
python prepare_company_data.py
```

### 2️⃣ Recommending Skills & Certifications
The `/url` endpoint in `user_backend.py` can be used to recommend skills and certifications. This can be run locally with `uvicorn`:
```bash
uvicorn user_backend:app --reload
```

Then, send a POST request:
```bash
curl -X POST "http://127.0.0.1:8000/url" -H "Content-Type: application/json" -d '{"url": "https://www.linkedin.com/in/sample-profile"}'
```

### 3️⃣ Ranking Contestants
To process contestant rankings, start the HR backend:
```bash
uvicorn hr_backend:app --reload
```

Then, send a request to `/process-csv/` with two CSV files:
```bash
curl -X POST "http://127.0.0.1:8000/process-csv/" -F "file1=@path/to/employees.csv" -F "file2=@path/to/contestants.csv"
```
The response will contain a downloadable CSV file with contestants ranked by similarity.

---

## 🤝 Acknowledgments

This project uses:
- The [LinkedIn API](https://linkedin-api.readthedocs.io/en/latest/) for data retrieval.
- The [Sentence Transformers](https://www.sbert.net/) model for profile similarity scoring.

