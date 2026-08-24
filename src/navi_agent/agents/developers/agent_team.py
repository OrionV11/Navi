from .code_writer import CodeWriter
from .debugger import Debugger
from .reviewer import Reviewer
import os

class AgentTeam:
    """Orchestrate multiple agents for complex coding tasks"""
    
    def __init__(self):
        self.writer = CodeWriter()
        self.debugger = Debugger()
        self.reviewer = Reviewer()
        self.output_dir = "generated_code"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_and_review_code(self, task: str, save_to_file: bool = True):
        """
        Full workflow: Generate → Debug → Review
        
        Args:
            task: Code generation task
            save_to_file: Save generated code to file
        
        Returns:
            dict with code, debug results, and review
        """
        print("\n" + "="*60)
        print("Step 1: Writing Code")
        print("="*60)
        code = self.writer.run(task)
        print(code)
        
        print("\n" + "="*60)
        print("Step 2: Debugging Code")
        print("="*60)
        debug_result = self.debugger.run(f"Test and debug this code:\n{code}")
        print(debug_result)
        
        print("\n" + "="*60)
        print("Step 3: Reviewing Code")
        print("="*60)
        review_result = self.reviewer.run(f"Review and improve this code:\n{code}")
        print(review_result)
        
        # Save to file if requested
        if save_to_file:
            filename = self._save_code(task, code)
            print(f"\nCode saved to: {filename}")
        
        return {
            "task": task,
            "code": code,
            "debug": debug_result,
            "review": review_result
        }
    
    def write_and_debug(self, task: str):
        """Write code and debug (skip review)"""
        print("\n" + "="*60)
        print("Step 1: Writing Code")
        print("="*60)
        code = self.writer.run(task)
        print(code)
        
        print("\n" + "="*60)
        print("Step 2: Debugging Code")
        print("="*60)
        debug_result = self.debugger.run(f"Test this code:\n{code}")
        print(debug_result)
        
        return {"code": code, "debug": debug_result}
    
    def review_existing_code(self, code: str):
        """Review code without generating"""
        print("\n" + "="*60)
        print("Reviewing Code")
        print("="*60)
        result = self.reviewer.run(f"Review this code:\n{code}")
        print(result)
        return result
    
    def fix_broken_code(self, code: str, error: str):
        """Debug broken code and regenerate fix"""
        print("\n" + "="*60)
        print("🔧 Fixing Broken Code")
        print("="*60)
        
        # Debug the error
        print("\nAnalyzing error...")
        debug_task = f"Fix this broken code:\n{code}\n\nError: {error}"
        fixed_code = self.debugger.run(debug_task)
        print(fixed_code)
        
        # Review the fix
        print("\nReviewing fix...")
        review = self.reviewer.run(f"Review this fixed code:\n{fixed_code}")
        print(review)
        
        return {"original": code, "error": error, "fixed": fixed_code, "review": review}
    
    def optimize_code(self, code: str):
        """Optimize and improve existing code"""
        print("\n" + "="*60)
        print("Optimizing Code")
        print("="*60)
        
        task = f"Optimize and improve this code for performance and readability:\n{code}"
        optimized = self.writer.run(task)
        print(optimized)
        
        # Review the optimized version
        print("\nReviewing optimized code...")
        review = self.reviewer.run(f"Review this optimized code:\n{optimized}")
        print(review)
        
        return {"original": code, "optimized": optimized, "review": review}
    
    def create_with_tests(self, task: str):
        """Generate code with test cases"""
        print("\n" + "="*60)
        print("Generating Code with Tests")
        print("="*60)
        
        # Generate code
        print("\nWriting code...")
        code = self.writer.run(task)
        print(code)
        
        # Generate tests
        print("\nCreating test cases...")
        test_task = f"Write unit tests for this code:\n{code}"
        tests = self.writer.run(test_task)
        print(tests)
        
        # Debug both
        print("\nTesting code...")
        debug_result = self.debugger.run(f"Test this code and tests:\n{code}\n\nTests:\n{tests}")
        print(debug_result)
        
        # Review
        print("\nReviewing...")
        review = self.reviewer.run(f"Review this code and tests:\n{code}\n\nTests:\n{tests}")
        print(review)
        
        return {"code": code, "tests": tests, "debug": debug_result, "review": review}
    
    def refactor_code(self, code: str, goal: str = "improve readability and performance"):
        """Refactor code with a specific goal"""
        print("\n" + "="*60)
        print("Refactoring Code")
        print("="*60)
        
        # Refactor
        print(f"\nRefactoring to {goal}...")
        refactor_task = f"Refactor this code to {goal}:\n{code}"
        refactored = self.writer.run(refactor_task)
        print(refactored)
        
        # Debug
        print("\nTesting refactored code...")
        debug_result = self.debugger.run(f"Test this refactored code:\n{refactored}")
        print(debug_result)
        
        # Review
        print("\nReviewing...")
        review = self.reviewer.run(f"Compare original and refactored:\n\nOriginal:\n{code}\n\nRefactored:\n{refactored}")
        print(review)
        
        return {"original": code, "refactored": refactored, "debug": debug_result, "review": review}
    
    def _save_code(self, task: str, code: str) -> str:
        """Save generated code to file"""
        # Create filename from task
        filename = task.replace(" ", "_").lower()[:30] + ".py"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"# Task: {task}\n")
            f.write(f"# Generated by Navi Agent Team\n\n")
            f.write(code)
        
        return filepath

# Usage
if __name__ == "__main__":
    team = AgentTeam()
    
    # Example 1: Full workflow
    print("\n\nEXAMPLE 1: Full Workflow (Generate → Debug → Review)")
    team.generate_and_review_code("Create a function that finds the nth Fibonacci number")
    
    # Example 2: Write and debug only
    # print("\n\nEXAMPLE 2: Write and Debug")
    # team.write_and_debug("Write a function to check if a string is a palindrome")
    
    # Example 3: Create with tests
    # print("\n\nEXAMPLE 3: Generate with Unit Tests")
    # team.create_with_tests("Create a Calculator class with add, subtract, multiply, divide methods")
