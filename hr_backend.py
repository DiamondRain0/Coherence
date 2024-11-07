from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import pandas as pd
import csv
from io import StringIO, BytesIO
from sentence_transformers import SentenceTransformer, util
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the pre-trained model
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Helper function to concatenate fields
def concatenate_fields(row):
    try:
        fields = [
            str(row.get('Occupation', '')),
            str(row.get('Company', '')),
            str(row.get('Certifications', '')),
            str(row.get('Skills', '')),
            str(row.get('Industry', '')),
            str(row.get('Experience', ''))
        ] 
        concatenated = " ".join([field for field in fields if field])
        return concatenated
    except Exception as e:
        print(f"Error concatenating fields: {e}")
        return ""

# Function to calculate the weighted average
def calculate_weighted_average(values):
    n = len(values)
    first_part = int(0.3 * n)
    next_part = int(0.5 * n)
    weights = [5] * first_part + [3] * next_part + [1] * (n - (first_part + next_part))
    weighted_sum = sum(value * weight for value, weight in zip(values, weights))
    total_weight = sum(weights)
    return weighted_sum / total_weight

@app.post("/process-csv/")
async def process_csv(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    # Read both CSV files into pandas DataFrames
    profiles_content = await file1.read()  # Use await here
    contestants_content = await file2.read()  # Use await here
    
    profiles_df = pd.read_csv(StringIO(profiles_content.decode('utf-8')))
    contestants_df = pd.read_csv(StringIO(contestants_content.decode('utf-8')))
    
    # Extract profiles and compute embeddings
    profiles = [concatenate_fields(row) for _, row in profiles_df.iterrows() if concatenate_fields(row)]
    profile_embeddings = model.encode(profiles, convert_to_tensor=True)
    
    output_data = []
    
    # Process each contestant and compute similarity
    for _, contestant_row in contestants_df.iterrows():
        contestant_name = contestant_row.get('Name', 'Unknown Name')
        source_sentence = concatenate_fields(contestant_row)
        source_embedding = model.encode(source_sentence, convert_to_tensor=True)
        
        # Compute similarities
        similarities = util.cos_sim(source_embedding, profile_embeddings)
        similarities_list = similarities[0].tolist()
        
        output_data.append([contestant_name, similarities_list])
    
    # Create a DataFrame for output
    output_df = pd.DataFrame(output_data, columns=['Contestant Name', 'Model Output'])
    
    # Apply the weighted average function and sort by it
    output_df['Weighted Average'] = output_df['Model Output'].apply(lambda x: calculate_weighted_average([float(i) for i in x]))
    df_sorted = output_df[['Contestant Name', 'Weighted Average']].sort_values(by='Weighted Average', ascending=False)

    # Convert the sorted DataFrame to CSV for download
    output = BytesIO()
    df_sorted.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sorted-contestants.csv"})
