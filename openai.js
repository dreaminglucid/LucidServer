// openai.js
require('dotenv').config();
const axios = require('axios');
const openai = require('openai');

const openai_api_key = process.env.OPENAI_API_KEY;
const openai_chat_url = "https://api.openai.com/v1/chat/completions";
const openai_image_url = "https://api.openai.com/v1/images/generations";

openai.api_key = openai_api_key;

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
      max_tokens: 60,
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

const getDreamImage = async (dreams, dreamId) => {
  try {
    const dream = dreams.find((d) => d.id === dreamId);
    if (!dream) {
      return null;
    }

    const summary = await getDreamSummary(dream.entry);

    const data = {
      prompt: `${summary}, high quality, digital art, photorealistic style, very detailed, lucid dream themed`,
      n: 1,
      size: '512x512',
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

module.exports = {
  getDreamSummary,
  getDreamImage,
  getGptResponse,
};