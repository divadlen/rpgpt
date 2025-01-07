# ALL DOCUMENTATIONS IS INCLUDED IN THIS PAGE

# Folders
## app
### apps 
Contains all the apps deployed to streamlit

### assets
Contains all the media and static files like logo, images, preset tables.

### utils
Contains all helper functions imported and used by app

### main.py
The main app file used by streamlit

### requirements.txt
The required packages to run the app and be deployed on streamlit

### Secrets
To run the app locally, you need to create a secrets.toml file in the root folder of the project.

API_KEY = st.secrets["API_KEY"]
```
# dir
ROOT/
├── main.py
├── apps
│   ├── app.py
│   ├── app-1.py
├── .streamlit <<< create this folder in local
|   ├── secrets.toml <<< create this file in local 
```
```
secrets.toml
API_KEY=your-api-key
```

To run the app on streamlit cloud, your secrets should be filled in the app settings. 

### Utils and helper functions
Read the doc string for each function to know what it does.

## notebooks
Notebooks to test the AI and RAG backend


# Using the app
1. Filter the original data
2. Get the filtered questions
3. Fill in the answers
4. Progress can be saved and loaded with 'settings.json' and 'qa_data.json' 
5. No auto filling of answers by feature yet (problem 8)
6. No auto verification of answers by feature yet (problem 8)
7. AI chat setup intention is to verify the ability to connect an AI backend to the app. The endgoal is suppose to allow the AI backend to interact with user uploads
8. Minimal vectorization of user upload feature implemented for now

