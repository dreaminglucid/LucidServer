// server.js
const express = require('express');
const cors = require('cors');
const database = require('./database');

const app = express();
const port = 5000;

require('dotenv').config();

app.use(cors());
app.use(express.json());

app.post('/api/dreams', async (req, res) => {
  const { title, date, entry } = req.body;
  const dream = await database.createDream(title, date, entry);
  if (dream !== null) {
    res.status(200).json(dream);
  } else {
    res.status(500).json({ error: 'Failed to save dream' });
  }
});

app.put('/api/dreams/:dreamId', async (req, res) => {
  const dreamId = parseInt(req.params.dreamId);
  const { analysis, image } = req.body;
  // server.js continued...
  const updatedDream = await database.updateDreamAnalysisAndImage(dreamId, analysis, image);
  if (updatedDream !== null) {
    res.status(200).json(updatedDream);
  } else {
    res.status(500).json({ error: 'Failed to update dream analysis and image' });
  }
});

app.get('/api/dreams', async (req, res) => {
  const allDreams = await database.getDreams();
  res.status(200).json(allDreams);
});

app.get('/api/dreams/:dreamId', async (req, res) => {
  const dreamId = parseInt(req.params.dreamId);
  const allDreams = await database.getDreams();
  const dream = allDreams.find((d) => d.id === dreamId);
  if (dream) {
    res.status(200).json(dream);
  } else {
    res.status(404).json({ error: 'Dream not found' });
  }
});

app.get('/api/dreams/:dreamId/analysis', async (req, res) => {
  const dreamId = parseInt(req.params.dreamId);
  const analysisResult = await database.getDreamAnalysis(dreamId);
  if (analysisResult !== null) {
    res.status(200).send(analysisResult);
  } else {
    res.status(404).json({ error: 'Dream not found' });
  }
});

app.get('/api/dreams/:dreamId/image', async (req, res) => {
  const dreamId = parseInt(req.params.dreamId);
  const dream = database.getDreams().find((d) => d.id === dreamId);
  if (dream && dream.image) {
    res.status(200).json({ image: dream.image });
  } else {
    res.status(404).json({ error: 'Dream image not found' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});