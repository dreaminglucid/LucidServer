# Lucid Journal backend server
The Lucid Journal backend server of the project is responsible for managing dream data, analyzing dream entries, and generating dream-inspired images using AI models like GPT-3.5/4 and DALLE 2.

![image](resources\banner.png)

## Packages
We utilize several agent-centric python packages from the [Autonomous Research Group](https://github.com/AutonomousResearchGroup).

- https://github.com/AutonomousResearchGroup/agentmemory
- https://github.com/AutonomousResearchGroup/easycompletion
- https://github.com/AutonomousResearchGroup/agentlogger

### Setup
To set up the Lucid Journal backend server, follow these steps:

1. Install Python: Visit the official Python website and download the latest version of Python for your operating system.

2. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

3. Create a "config.ini" file: In the same directory as the API code, create a "config.ini" file and add the following content:
   ```
   [openai]
   api_key=YOUR_OPENAI_API_KEY
   ```
   Replace "YOUR_OPENAI_API_KEY" with your actual OpenAI API key.

### Running the API with ngrok
To expose the API locally and access it from the Dream Guide app running on Expo, you can use ngrok. Follow these steps:

1. Install ngrok: Visit the ngrok website and download the appropriate version for your operating system.

2. In the terminal, navigate to the directory containing the Lucid Journal backend server.

3. Run the command to start ngrok and forward requests to the local API server on port 5000:
   ```
   ngrok http 5000
   ```

4. ngrok will generate a temporary public URL (e.g., `http://xxxxxxx.ngrok.io`) that forwards requests to your local API server.

### API Endpoints
The Lucid Journal backend server provides several endpoints to interact with dream data and AI models. Some key endpoints include:

- **POST /api/dreams**: Create a new dream entry.
- **PUT /api/dreams/{dream_id}**: Update the analysis and image of a specific dream entry.
- **GET /api/dreams**: Get all saved dream entries.
- **GET /api/dreams/{dream_id}**: Get details of a specific dream entry.
- **GET /api/dreams/{dream_id}/analysis**: Get the analysis of a specific dream entry.
- **GET /api/dreams/{dream_id}/image**: Get the AI-generated dream-inspired image for a specific dream entry.
- **POST /api/chat**: Have interactive conversations with the AI dream guide.
- **POST /api/dreams/search**: Search for dream entries based on keywords.
- **POST /api/dreams/search-chat**: Have AI-guided conversations with the AI dream guide and relevant dream entries found in the database.

### Running the API
To start the API server, execute the following command:

```
python server.py
```

By default, the API will run on `http://127.0.0.1:5000/`, and you can make requests to the API using tools like Postman or integrate it into your own applications.

## Heroku Deploy

### Constraints
- **Slug Size Limit**: Slugs can't be larger than 500MB. If the slug is too large, consider using Docker or reducing the content included in the slug.
- **Memory Limit**: Memory cannot exceed 500MB for a single dyno. Monitor and optimize memory usage as needed.
- **Dynamic Model Import**: Models will be dynamically imported and used at runtime to keep the slug size manageable.
- **Docker Deployment**: If the slug is too large, consider deploying with a Dockerfile instead of a Procfile.

### Tutorials
- [Getting Started with Heroku](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Deploying with Docker on Heroku](https://devcenter.heroku.com/categories/deploying-with-docker)
- [Heroku Slug Compiler](https://devcenter.heroku.com/articles/slug-compiler)

### Commands
- `heroku create` (create a new Heroku app)
- `heroku stack:set heroku-22` (set stack for Procfile deployment)
- `heroku stack:set container` (set stack for Dockerfile deployment)
- `git push heroku main` (push code to Heroku and start build)
- `heroku logs --tail` (view build and runtime logs)
- `heroku config:set KEY=VALUE` (set environment variables via Heroku CLI)

### Environment Variables
Must set ENV variables in Heroku dashboard or with Heroku CLI tool:

```bash
CLIENT_TYPE='POSTGRES'
POSTGRES_CONNECTION_STRING=YOUR_URI_CONNECTION_STRING
```