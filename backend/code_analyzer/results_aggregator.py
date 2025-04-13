from typing import Dict, Any

class ResultsAggregator:
    """
    A simple results aggregator that passes through the AI-generated responses
    without complex processing.
    """
    def __init__(self):
        pass
        
    def aggregate_results(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simply return the AI-generated results for direct consumption by the frontend.
        The AI responses are already well-structured based on our prompts.
        
        Args:
            analysis_results: Raw results from the AI analysis
            
        Returns:
            The same results with minimal processing
        """
        return {
            'semantic_analysis': analysis_results['semantic_analysis'],
            'correctness_analysis': analysis_results['correctness_analysis'],
            'edge_cases': analysis_results['edge_cases'],
            'test_cases': analysis_results['test_cases']
        }