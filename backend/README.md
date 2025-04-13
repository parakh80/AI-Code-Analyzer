# AI-Based Code Correctness Assessment System

This project implements an AI-powered system for analyzing and assessing code correctness, quality, and generating test cases. It uses Google's Gemini models to provide intelligent analysis of Python and JavaScript code.

## Features

- Code processing and chunking
- Semantic understanding of code purpose
- Code quality assessment
- Logical flaw detection
- Edge case identification
- Test case generation
- Support for multiple languages (Python, JavaScript)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Project Structure

- `code_analyzer/`
  - `__init__.py`: Package initialization
  - `code_processor.py`: Code processing and chunking
  - `ai_analyzer.py`: AI integration and analysis
  - `pipeline.py`: Analysis pipeline orchestration
  - `results_aggregator.py`: Combine results from analysis stages
- `api.py`: FastAPI backend service
- `requirements.txt`: Project dependencies

## Usage

1. Start the API server:
```bash
uvicorn api:app --reload
```

2. Use the API endpoints to submit code for analysis:
   - `/analyze`: Submit code for analysis
   - `/status/{analysis_id}`: Check analysis status
   - `/results/{analysis_id}`: Get analysis results

The system will:
1. Process your code into logical chunks
2. Analyze each chunk for:
   - Code purpose
   - Quality assessment
   - Correctness evaluation
   - Test case generation

## Example Output

The system provides detailed analysis for each code submission, including:
- Purpose inference
- Quality assessment
- Correctness evaluation
- Edge case identification
- Generated test cases

## Requirements

- Python 3.8+
- Google Gemini API key
- Dependencies listed in requirements.txt

## License

MIT License