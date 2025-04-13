# import importlib.util
# import sys
# from typing import Dict, List, Any, Optional
# from dataclasses import dataclass
# from .response_parser import TestCase

# @dataclass
# class TestResult:
#     test_case: TestCase
#     passed: bool
#     actual_output: Any
#     error: Optional[str] = None
#     execution_time: Optional[float] = None

# class TestRunner:
#     def __init__(self, module_path: str):
#         self.module_path = module_path
#         self.module = self._load_module()

#     def _load_module(self) -> Any:
#         """Load the Python module to test."""
#         spec = importlib.util.spec_from_file_location("module_to_test", self.module_path)
#         if spec is None or spec.loader is None:
#             raise ImportError(f"Could not load module from {self.module_path}")
        
#         module = importlib.util.module_from_spec(spec)
#         sys.modules["module_to_test"] = module
#         spec.loader.exec_module(module)
#         return module

#     def _execute_test(self, test_case: TestCase) -> TestResult:
#         """Execute a single test case."""
#         try:
#             # Get the function to test
#             func_name = test_case.input_data.get('function', '')
#             if not func_name:
#                 return TestResult(
#                     test_case=test_case,
#                     passed=False,
#                     actual_output=None,
#                     error="No function specified in test case"
#                 )

#             func = getattr(self.module, func_name, None)
#             if func is None:
#                 return TestResult(
#                     test_case=test_case,
#                     passed=False,
#                     actual_output=None,
#                     error=f"Function {func_name} not found in module"
#                 )

#             # Prepare input arguments
#             args = []
#             kwargs = {}
#             for key, value in test_case.input_data.items():
#                 if key != 'function':
#                     if key.startswith('arg'):
#                         args.append(eval(value))
#                     else:
#                         kwargs[key] = eval(value)

#             # Execute the test
#             import time
#             start_time = time.time()
#             actual_output = func(*args, **kwargs)
#             execution_time = time.time() - start_time

#             # Compare with expected output
#             expected_output = eval(test_case.expected_output)
#             passed = self._compare_outputs(actual_output, expected_output)

#             return TestResult(
#                 test_case=test_case,
#                 passed=passed,
#                 actual_output=actual_output,
#                 execution_time=execution_time
#             )

#         except Exception as e:
#             return TestResult(
#                 test_case=test_case,
#                 passed=False,
#                 actual_output=None,
#                 error=str(e)
#             )

#     def _compare_outputs(self, actual: Any, expected: Any) -> bool:
#         """Compare actual and expected outputs."""
#         if isinstance(expected, float):
#             # Use relative tolerance for floating point comparison
#             return abs(actual - expected) < 1e-9
#         return actual == expected

#     def run_tests(self, test_cases: List[TestCase]) -> List[TestResult]:
#         """Run a list of test cases."""
#         results = []
#         for test_case in test_cases:
#             result = self._execute_test(test_case)
#             results.append(result)
#         return results

#     def get_test_summary(self, results: List[TestResult]) -> Dict[str, Any]:
#         """Generate a summary of test results."""
#         total = len(results)
#         passed = sum(1 for r in results if r.passed)
#         failed = total - passed
        
#         by_category = {
#             'normal': {'total': 0, 'passed': 0},
#             'edge': {'total': 0, 'passed': 0},
#             'error': {'total': 0, 'passed': 0}
#         }
        
#         for result in results:
#             category = result.test_case.category
#             by_category[category]['total'] += 1
#             if result.passed:
#                 by_category[category]['passed'] += 1
        
#         return {
#             'total_tests': total,
#             'passed_tests': passed,
#             'failed_tests': failed,
#             'pass_rate': (passed / total) * 100 if total > 0 else 0,
#             'by_category': by_category
#         } 