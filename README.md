# AI Code Analyzer

## Project Description

AI Code Analyzer is a web application built to analyze code snippets currently supporting Python and JavaScript using the power of Google’s Gemini AI models. It offers insights into code correctness, uncovers potential edge cases, performs deep semantic analysis, and auto-generates relevant test cases. With a clean and user-friendly interface, users can easily submit their code and track progress while reviewing detailed analysis results.

While this tool doesn't replace prompt engineers, it significantly boosts their productivity. It helps them better understand AI-generated code, spot edge-case errors that might be missed during manual analysis, and leverage test cases to validate the logic. It’s all about making prompt engineering smarter, faster, and more reliable.

## Features

*   **AI-Powered Analysis:** Leverages the Gemini API for deep code understanding.
*   **Multiple Analysis Types:**
    *   Correctness Assessment
    *   Edge Case Identification
    *   Semantic Understanding
    *   Test Case Generation
*   **Language Support:** Analyzes Python and JavaScript code.
*   **Web Interface:** Built with Next.js and React for a smooth user experience.
*   **Code Editor:** Integrated Monaco Editor for code input.
*   **Markdown Results:** Displays analysis results in a formatted Markdown view with syntax highlighting.
*   **Real-time Progress:** Shows the analysis progress step-by-step.
*   **API Key Protection:** Secures the backend API endpoint.

## Tech Stack

*   **Backend:**
    *   Python 3.x
    *   FastAPI
    *   Uvicorn (ASGI Server)
    *   Google Genai SDK (`google-generativeai`)
    *   `python-dotenv`
*   **Frontend:**
    *   Node.js
    *   React
    *   Next.js
    *   TypeScript
    *   Tailwind CSS
    *   Monaco Editor (`@monaco-editor/react`)
    *   `react-markdown`
    *   `react-syntax-highlighter`
*   **AI Model:** Google Gemini API

## Setup Instructions

### Prerequisites

*   Git ([https://git-scm.com/downloads](https://git-scm.com/downloads))
*   Python 3.8+ and Pip ([https://www.python.org/downloads/](https://www.python.org/downloads/))
*   Node.js and npm (or yarn) ([https://nodejs.org/](https://nodejs.org/))
*   A Google Gemini API Key ([https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey))

### Installation

1.  **Clone the Repository (if applicable):**
    *(If you haven't cloned it yet, otherwise skip)*
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Backend Setup:**
    *   Navigate to the backend directory:
        ```bash
        cd backend
        ```
    *   Create and activate a virtual environment (recommended):
        ```bash
        # Windows
        python -m venv venv
        .\venv\Scripts\activate

        # macOS/Linux
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   Install Python dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Create a `.env` file in the `backend` directory and add your API keys:
        ```dotenv
        # backend/.env
        GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
        API_KEY=YOUR_CHOSEN_BACKEND_API_KEY # Optional: A secret key clients must send (e.g., 'mysecretkey')
        ```
        *(Replace `YOUR_GEMINI_API_KEY_HERE` with your actual key. Set `API_KEY` to a secret value if you want to protect the backend endpoint).*

3.  **Frontend Setup:**
    *   Navigate to the frontend directory from the project root:
        ```bash
        cd ../frontend
        # Or if you are in the backend dir: cd ../frontend
        ```
    *   Install Node.js dependencies:
        ```bash
        npm install
        # or
        yarn install
        ```
    *   Create a `.env.local` file in the `frontend` directory and configure the backend URL:
        ```dotenv
        # frontend/.env.local
        NEXT_PUBLIC_API_URL=http://localhost:8000
        # Optional: If you set an API_KEY in the backend .env, add it here
        NEXT_PUBLIC_BACKEND_API_KEY=YOUR_CHOSEN_BACKEND_API_KEY
        ```
        *(Ensure `NEXT_PUBLIC_API_URL` points to where your backend will run. Add `NEXT_PUBLIC_BACKEND_API_KEY` only if you set `API_KEY` in the backend).*

## Running the Project

1.  **Start the Backend Server:**
    *   Open a terminal in the `backend` directory.
    *   Make sure your virtual environment is activated.
    *   Run the FastAPI application:
        ```bash
        python api.py
        ```
    *   The backend should now be running, typically at `http://localhost:8000`.

2.  **Start the Frontend Development Server:**
    *   Open a *separate* terminal in the `frontend` directory.
    *   Run the Next.js development server:
        ```bash
        npm run dev
        # or
        yarn dev
        ```
    *   The frontend should now be running, typically at `http://localhost:3000`.

3.  **Access the Application:**
    *   Open your web browser and navigate to `http://localhost:3000`.

## Usage

1.  Open the application in your browser.
2.  Select the programming language (Python or JavaScript) from the dropdown.
3.  Paste your code snippet into the editor.
4.  Click the "Analyze Code" button.
5.  Observe the progress bar and status messages as the analysis runs.
6.  View the detailed analysis results (Correctness, Edge Cases, Semantic Analysis, Test Cases) displayed in the results panel.

---
