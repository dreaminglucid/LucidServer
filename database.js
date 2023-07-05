// database.js
const fs = require('fs');
const path = require('path');
const openai = require('./openai');

const dreamsFilePath = path.join(__dirname, 'dreams.json');
let dreams = [];

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

    const analysisResult = await openai.getGptResponse(dream.entry, 'Dream analysis system message');
    return analysisResult;
  } catch (error) {
    console.error('Error analyzing dream:', error);
    return null;
  }
};

module.exports = {
  readDreamsFromFile,
  writeDreamsToFile,
  createDream,
  updateDreamAnalysisAndImage,
  getDreams,
  getDreamAnalysis,
};