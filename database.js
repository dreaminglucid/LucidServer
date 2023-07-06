// database.js
const openai = require('./openai');
const { OpenAIEmbeddingFunction, ChromaClient } = require('chromadb');

// Initialize the OpenAIEmbeddingFunction
const embeddingFunction = new OpenAIEmbeddingFunction({ openai_api_key: process.env.OPENAI_API_KEY });

// Initialize the ChromaClient
const client = new ChromaClient('http://localhost:8000');

(async () => {
  try {
    let collection = await client.getCollection({ name: 'dreams', embeddingFunction });
    if (!collection) {
      await client.createCollection({ name: 'dreams', embeddingFunction });
    }
  } catch (error) {
    console.error('Error initializing dreams collection:', error);
  }
})();

let dreams = [];

const createDream = async (title, date, entry) => {
  try {
    const embeddings = await embeddingFunction.generate([entry]); // Generate embeddings for the dream entry
    const dream = { id: dreams.length + 1, title, date, entry, embeddings: embeddings[0] };
    dreams.push(dream);

    const collection = await client.getCollection({ name: 'dreams', embeddingFunction });
    if (!collection) {
      throw new Error('Failed to initialize dreams collection');
    }
    // Use upsert method to add or update the dream in the collection
    await collection.upsert({ ids: [dream.id.toString()], embeddings: [dream.embeddings], documents: [JSON.stringify(dream)] });

    return dream;
  } catch (error) {
    console.error('Error saving dream:', error);
    return null;
  }
};

const getDreams = async () => {
  try {
    const collection = await client.getCollection({ name: 'dreams', embeddingFunction });
    if (!collection) {
      throw new Error('Failed to initialize dreams collection');
    }
    const results = await collection.get({ include: ['embeddings', 'metadatas', 'documents'] });
    console.log('getDreams results:', results); // Add this line
    if (results.documents) {
      return results.documents.map(doc => doc ? JSON.parse(doc) : null);
    } else {
      throw new Error('No dreams found');
    }
  } catch (error) {
    console.error('Error getting dreams:', error);
    return [];
  }
};

const updateDreamAnalysisAndImage = async (dreamId, analysis, image) => {
  try {
    const dream = dreams.find((d) => d.id === dreamId);
    if (!dream) {
      return null;
    }

    dream.analysis = analysis;
    dream.image = image;

    // Update the embeddings after updating the dream analysis
    const embeddings = await embeddingFunction.generate([dream.entry]);
    dream.embeddings = embeddings[0];

    // Update the collection in ChromaDB for the updated dream
    const collection = await client.getCollection({ name: `dream_${dream.id}`, embeddingFunction });
    await collection.upsert({ ids: [dream.id.toString()], embeddings: [dream.embeddings], documents: [dream] });

    return dream;
  } catch (error) {
    console.error('Error updating dream analysis and image:', error);
    return null;
  }
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
  createDream,
  updateDreamAnalysisAndImage,
  getDreams,
  getDreamAnalysis,
};