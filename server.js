const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const openai = require('openai');

const app = express();
const port = 5000;

app.use(cors());
app.use(express.json());

const dreamsFilePath = path.join(__dirname, 'dreams.json');
let dreams = [];

const openai_api_key = "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";
const openai_chat_url = "https://api.openai.com/v1/chat/completions";
const openai_image_url = "https://api.openai.com/v1/images/generations";

openai.api_key = openai_api_key;

const readDreamsFromFile = () => {
  try {
    const fileContent = fs.readFileSync(dreamsFilePath, 'utf-8');
    dreams = JSON.parse(fileContent);
  } catch (error) {
    console.error('Error reading dreams from file:', error);
    dreams = [];
  }
};

const writeDreamsToFile = () => {
  try {
    fs.writeFileSync(dreamsFilePath, JSON.stringify(dreams, null, 2), 'utf-8');
  } catch (error) {
    console.error('Error writing dreams to file:', error);
  }
};

const createDream = (title, date, entry) => {
  try {
    const dream = { id: dreams.length + 1, title, date, entry, analysis: '', image: null };
    dreams.push(dream);
    writeDreamsToFile();
    return dream;
  } catch (error) {
    console.error('Error saving dream:', error);
    return null;
  }
};

const updateDreamAnalysisAndImage = (dreamId, analysis, image) => {
  try {
    const dream = dreams.find((d) => d.id === dreamId);
    if (!dream) {
      return null;
    }

    dream.analysis = analysis;
    dream.image = image;
    writeDreamsToFile();
    return dream;
  } catch (error) {
    console.error('Error updating dream analysis and image:', error);
    return null;
  }
};

const getDreams = () => {
  return dreams;
};

const getDreamAnalysis = async (dreamId) => {
  try {
    const dream = dreams.find((d) => d.id === dreamId);
    if (!dream) {
      return null;
    }

    const analysisResult = await getGptResponse(dream.entry, 'Dream analysis system message');
    return analysisResult;
  } catch (error) {
    console.error('Error analyzing dream:', error);
    return null;
  }
};

const getDreamSummary = async (dreamEntry) => {
  try {
    const response = await axios.post(openai_chat_url, {
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'Please summarize the following text to be used as the perfect DALLE 2 openai prompt:',
        },
        {
          role: 'user',
          content: dreamEntry,
        },
      ],
      max_tokens: 60, // Adjust this value based on how short you want the summary to be
    }, {
      headers: {
        'Authorization': `Bearer ${openai_api_key}`,
        'Content-Type': 'application/json',
      },
    });

    const choices = response.data.choices;
    if (choices && choices.length > 0) {
      const aiResponse = choices[0].message.content.trim();
      return aiResponse;
    } else {
      return 'Error: Unable to generate a summary.';
    }
  } catch (error) {
    console.error('Error generating GPT summary:', error);
    return 'Error: Unable to generate a summary.';
  }
};

const getDreamImage = async (dreamId) => {
  try {
    const dream = dreams.find((d) => d.id === dreamId);
    if (!dream) {
      return null;
    }

    const summary = await getDreamSummary(dream.entry);

    const data = {
      prompt: `${summary}, high quality, digital art, photorealistic style, very detailed, lucid dream themed`,
      n: 1,
      size: '1024x1024',
    };
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${openai_api_key}`,
    };
    const response = await axios.post(openai_image_url, data, { headers });
    const imageData = response.data.data[0];
    return imageData;
  } catch (error) {
    console.error('Error generating dream-inspired image:', error);
    throw error;
  }
};

const getGptResponse = async (prompt, systemContent) => {
  try {
    const response = await axios.post(openai_chat_url, {
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: systemContent,
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      max_tokens: 333,
    }, {
      headers: {
        'Authorization': `Bearer ${openai_api_key}`,
        'Content-Type': 'application/json',
      },
    });

    const choices = response.data.choices;
    if (choices && choices.length > 0) {
      const aiResponse = choices[0].message.content.trim();
      return aiResponse;
    } else {
      return 'Error: Unable to generate a response.';
    }
  } catch (error) {
    console.error('Error generating GPT response:', error);
    return 'Error: Unable to generate a response.';
  }
};

readDreamsFromFile();

app.post('/api/dreams', (req, res) => {
  const { title, date, entry } = req.body;
  const dream = createDream(title, date, entry);
  if (dream !== null) {
    res.status(200).json(dream);
  } else {
    res.status(500).json({ error: 'Failed to save dream' });
  }
});

app.put('/api/dreams/:dreamId', (req, res) => {
  const dreamId = parseInt(req.params.dreamId);
  const { analysis, image } = req.body;
  const updatedDream = updateDreamAnalysisAndImage(dreamId, analysis, image);
  if (updatedDream !== null) {
    res.status(200).json(updatedDream);
  } else {
    res.status(500).json({ error: 'Failed to update dream analysis and image' });
  }
});

app.get('/api/dreams', (req, res) => {
  const allDreams = getDreams();
  res.status(200).json(allDreams);
});

app.get('/api/dreams/:dreamId', (req, res) => {
  const dreamId = parseInt(req.params.dreamId);
  const dream = dreams.find((d) => d.id === dreamId);
  if (dream) {
    res.status(200).json(dream);
  } else {
    res.status(404).json({ error: 'Dream not found' });
  }
});

app.get('/api/dreams/:dreamId/analysis', async (req, res) => {
  const dreamId = parseInt(req.params.dreamId);
  const analysisResult = await getDreamAnalysis(dreamId);
  if (analysisResult !== null) {
    res.status(200).send(analysisResult);
  } else {
    res.status(404).json({ error: 'Dream not found' });
  }
});

app.get('/api/dreams/:dreamId/image', async (req, res) => {
  const dreamId = parseInt(req.params.dreamId);
  const imageData = await getDreamImage(dreamId);
  if (imageData !== null) {
    res.status(200).json(imageData);
  } else {
    res.status(404).json({ error: 'Dream not found' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});