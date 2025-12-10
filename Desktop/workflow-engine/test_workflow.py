"""
Simple test script to verify workflow functionality
Run with: python test_workflow.py
"""
import asyncio
from app.engine.workflow import WorkflowState
from app.workflows.code_review import create_code_review_workflow


async def test_code_review():
    """Test the code review workflow"""
    print("=" * 60)
    print("Testing Code Review Workflow")
    print("=" * 60)
    
    # Test case 1: Bad code
    bad_code = '''
def bad_function():
    for i in range(100):
        if i > 0:
            for j in range(100):
                if j > 0:
                    print(i * j)
    return True
'''
    
    print("\n📝 Test Case 1: Poor Quality Code")
    print("-" * 60)
    
    workflow = create_code_review_workflow().build()
    initial_state = WorkflowState(data={
        "code": bad_code,
        "quality_threshold": 70
    })
    
    final_state, logs = await workflow.run(initial_state)
    
    print(f"✓ Executed {len(logs)} steps")
    print(f"✓ Quality Score: {final_state.data.get('quality_score', 0)}")
    print(f"✓ Issues Found: {len(final_state.data.get('issues', []))}")
    print(f"✓ Suggestions: {len(final_state.data.get('suggestions', []))}")
    print(f"✓ Iterations: {final_state.data.get('iteration', 0)}")
    
    print("\n📋 Issues:")
    for issue in final_state.data.get("issues", []):
        print(f"  - {issue}")
    
    print("\n💡 Suggestions:")
    for suggestion in final_state.data.get("suggestions", []):
        print(f"  - {suggestion}")
    
    # Test case 2: Good code
    good_code = '''
def calculate_sum(numbers):
    """Calculate the sum of a list of numbers."""
    return sum(numbers)

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
'''
    
    print("\n" + "=" * 60)
    print("📝 Test Case 2: Good Quality Code")
    print("-" * 60)
    
    workflow2 = create_code_review_workflow().build()
    initial_state2 = WorkflowState(data={
        "code": good_code,
        "quality_threshold": 70
    })
    
    final_state2, logs2 = await workflow2.run(initial_state2)
    
    print(f"✓ Executed {len(logs2)} steps")
    print(f"✓ Quality Score: {final_state2.data.get('quality_score', 0)}")
    print(f"✓ Issues Found: {len(final_state2.data.get('issues', []))}")
    print(f"✓ Iterations: {final_state2.data.get('iteration', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ All Tests Passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_code_review()) 
