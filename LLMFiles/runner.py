import pandas as pd

# Load the CSV file
df = pd.read_csv('LLMFiles/demo-audio-data.csv')

# Print the first few rows to understand the structure
print(df.head())

# Assuming the CSV has a column named 'transcription', extract the transcription
transcription = df['transcription'].iloc[0]

# Print the transcription to verify
print(transcription)