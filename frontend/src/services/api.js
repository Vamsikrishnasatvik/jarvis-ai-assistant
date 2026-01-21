const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const chatAPI = {
  async sendMessage(message, conversationHistory = []) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_history: conversationHistory,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send message');
      }

      return await response.json();
    } catch (error) {
      console.error('Chat API error:', error);
      throw error;
    }
  },
};

export const knowledgeAPI = {
  async add(text, metadata = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/knowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, metadata }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add knowledge');
      }

      return await response.json();
    } catch (error) {
      console.error('Add knowledge error:', error);
      throw error;
    }
  },

  async list() {
    try {
      const response = await fetch(`${API_BASE_URL}/knowledge`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch knowledge');
      }

      return await response.json();
    } catch (error) {
      console.error('List knowledge error:', error);
      throw error;
    }
  },

  async delete(id) {
    try {
      const response = await fetch(`${API_BASE_URL}/knowledge/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete knowledge');
      }

      return await response.json();
    } catch (error) {
      console.error('Delete knowledge error:', error);
      throw error;
    }
  },

  async uploadFile(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload file');
      }

      return await response.json();
    } catch (error) {
      console.error('Upload file error:', error);
      throw error;
    }
  },
};