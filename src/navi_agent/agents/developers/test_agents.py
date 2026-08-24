#!/usr/bin/env python3
"""Test individual agents"""

from agents.code_writer import CodeWriter
from agents.debugger import Debugger
from agents.reviewer import Reviewer

def test_code_writer():
    print("\n" + "="*60)
    print("🔹 Testing CodeWriter Agent")
    print("="*60)
    agent = CodeWriter()
    result = agent.run("Write a function that reverses a string")
    print(result)

def test_debugger():
    print("\n" + "="*60)
    print("🐛 Testing Debugger Agent")
    print("="*60)
    agent = Debugger()
    result = agent.run("Debug: def add(a, b): return a + b")
    print(result)

def test_reviewer():
    print("\n" + "="*60)
    print("✅ Testing Reviewer Agent")
    print("="*60)
    agent = Reviewer()
    result = agent.run("Review: print(len([1, 2, 3]))")
    print(result)

if __name__ == "__main__":
    test_code_writer()
    test_debugger()
    test_reviewer()
