from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
import asyncio
from .code_processor import CodeProcessor
from .ai_analyzer import AIAnalyzer
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_code(file_path_or_code: str, mode: str = 'full', is_code_string: bool = False, language: str = 'python') -> Dict[str, Any]:
    """Analyze code using the analysis pipeline.
    
    Args:
        file_path_or_code: Path to the code file OR the code string itself
        mode: Analysis mode ('full', 'quick', or 'deep')
        is_code_string: If True, treat the first parameter as the code string, not a file path
        language: Programming language of the code ('python', 'javascript', etc.)
    """
    try:
        logger.info(f"Starting code analysis with mode: {mode}, language: {language}")
        pipeline = AnalysisPipeline(mode=mode, language=language)
        
        if is_code_string:
            results = pipeline.run_analysis_from_string(file_path_or_code)
        else:
            results = pipeline.run_analysis(file_path_or_code)
            
        logger.info("Analysis completed successfully")
        return results
    except Exception as e:
        logger.error(f"Analysis failed with error: {str(e)}")
        return {
            'error': str(e),
            'semantic_analysis': "Failed to analyze code semantics.",
            'correctness_analysis': "Failed to assess code correctness.",
            'edge_cases': "Failed to identify edge cases.",
            'test_cases': "Failed to generate test cases."
        }

class AnalysisPipeline:
    def __init__(self, mode: str = "full", language: str = 'python'):
        self.mode = mode
        self.language = language
        self.analyzer = AIAnalyzer()
        self.code_processor = CodeProcessor()
        logger.info(f"Initializing AnalysisPipeline with mode: {mode}, language: {language}")

    def analyze_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single code chunk."""
        try:
            # Ensure the language is included in the chunk context
            if 'context' in chunk and isinstance(chunk['context'], dict):
                chunk['context']['language'] = self.language
                
            logger.info(f"Starting chunk analysis for {self.language} code")
            
            # Semantic understanding
            logger.info("Analyzing code semantics")
            semantic_analysis = self.analyzer.analyze_semantics(chunk)
            
            # Correctness assessment
            logger.info("Assessing code correctness")
            correctness_analysis = self.analyzer.assess_correctness(chunk)
            
            # Edge case identification
            logger.info("Identifying edge cases")
            edge_cases = self.analyzer.identify_edge_cases(chunk)
            
            # Test case generation
            logger.info("Generating test cases")
            test_cases = self.analyzer.generate_test_cases(chunk)
            
            # Return raw responses for simplified processing
            return {
                'semantic_analysis': semantic_analysis.get('response', "No semantic analysis available."),
                'correctness_analysis': correctness_analysis.get('response', "No correctness analysis available."),
                'edge_cases': edge_cases.get('response', "No edge case analysis available."),
                'test_cases': test_cases.get('response', "No test cases available.")
            }
        except Exception as e:
            logger.error(f"Chunk analysis failed with error: {str(e)}")
            raise

    def process_code_string(self, code: str) -> Dict[str, Any]:
        """Process a code string directly and analyze its contents."""
        try:
            # Choose appropriate file extension based on language
            file_extension = ".js" if self.language == "javascript" else ".py"
            file_name = f"unnamed_code{file_extension}"
            
            logger.info(f"Processing {self.language} code string directly")
            
            # Use our code processor to chunk the code
            chunks = self.code_processor.process_code_string(code)
            
            # If no chunks were created by the processor, create a basic chunk
            if not chunks:
                chunks = [{
                    'code': code,
                    'context': {
                        'file_name': file_name,
                        'language': self.language,
                        'total_lines': len(code.split('\n'))
                    }
                }]
            
            logger.info(f"Code split into {len(chunks)} chunks")
            
            # Analyze chunks in parallel
            logger.info("Starting parallel chunk analysis")
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(self.analyze_chunk, chunks))
            
            # Simplify result aggregation - just combine results from all chunks
            logger.info("Aggregating results")
            
            # Combine results from all chunks
            combined_results = {
                'semantic_analysis': "\n\n".join([r['semantic_analysis'] for r in results]),
                'correctness_analysis': "\n\n".join([r['correctness_analysis'] for r in results]),
                'edge_cases': "\n\n".join([r['edge_cases'] for r in results]),
                'test_cases': "\n\n".join([r['test_cases'] for r in results])
            }
            
            return combined_results
        except Exception as e:
            logger.error(f"Code string processing failed with error: {str(e)}")
            raise

    def process_code(self, code_file: str) -> Dict[str, Any]:
        """Process the code file and analyze its contents."""
        try:
            logger.info(f"Processing code file: {code_file}")
            
            # Use the code processor to read and process the file
            chunks = self.code_processor.process_code_from_file(code_file)
            
            # If no chunks were created by the processor, fallback to reading the file directly
            if not chunks:
                # Read the code file
                with open(code_file, 'r') as f:
                    code = f.read()
                
                chunks = [{
                    'code': code,
                    'context': {
                        'file_name': os.path.basename(code_file),
                        'total_lines': len(code.split('\n'))
                    }
                }]
            
            logger.info(f"Code split into {len(chunks)} chunks")
            
            # Analyze chunks in parallel
            logger.info("Starting parallel chunk analysis")
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(self.analyze_chunk, chunks))
            
            # Simplify result aggregation - just combine results from all chunks
            logger.info("Aggregating results")
            
            # Combine results from all chunks
            combined_results = {
                'semantic_analysis': "\n\n".join([r['semantic_analysis'] for r in results]),
                'correctness_analysis': "\n\n".join([r['correctness_analysis'] for r in results]),
                'edge_cases': "\n\n".join([r['edge_cases'] for r in results]),
                'test_cases': "\n\n".join([r['test_cases'] for r in results])
            }
            
            return combined_results
        except Exception as e:
            logger.error(f"Code processing failed with error: {str(e)}")
            raise

    def run_analysis(self, code_file: str) -> Dict[str, Any]:
        """Run the complete analysis pipeline using a file path."""
        try:
            logger.info("Starting analysis pipeline for file")
            raw_results = self.process_code(code_file)
            
            # Use the simplified results aggregator
            from .results_aggregator import ResultsAggregator
            aggregator = ResultsAggregator()
            simplified_results = aggregator.aggregate_results(raw_results)
            
            logger.info("Analysis pipeline completed with simplified results")
            return simplified_results
        except Exception as e:
            logger.error(f"Analysis failed with error: {str(e)}")
            raise
            
    def run_analysis_from_string(self, code_string: str) -> Dict[str, Any]:
        """Run the complete analysis pipeline directly from a code string."""
        try:
            logger.info("Starting analysis pipeline for code string")
            raw_results = self.process_code_string(code_string)
            
            # Use the simplified results aggregator
            from .results_aggregator import ResultsAggregator
            aggregator = ResultsAggregator()
            simplified_results = aggregator.aggregate_results(raw_results)
            
            logger.info("Analysis pipeline completed with simplified results")
            return simplified_results
        except Exception as e:
            logger.error(f"Analysis failed with error: {str(e)}")
            raise