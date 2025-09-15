#!/usr/bin/env python3
"""
Test the improved RAG system with the corrected schema data.
"""
import os
import sys
import asyncio

# Set environment to use local Vanna
os.environ["USE_LOCAL_VANNA"] = "true"

async def test_improved_rag():
    """Test the improved RAG system."""
    print("🧪 Testing Improved RAG System")
    print("=" * 40)
    
    try:
        # Import the enhanced RAG system
        from app.infrastructure.enhanced_rag_system import EnhancedRAGSystem
        
        # Create RAG system
        rag_system = EnhancedRAGSystem(db_path="vanna_app_clean.db")
        
        # Initialize
        print("🔧 Initializing RAG system...")
        success = await rag_system.initialize()
        
        if not success:
            print("❌ RAG system initialization failed")
            return False
        
        print("✅ RAG system initialized successfully")
        
        # Test context retrieval
        test_questions = [
            "Show me users with their order count",
            "Calculate customer lifetime value",
            "What is the total sales amount?",
            "Show employees in Engineering department"
        ]
        
        for question in test_questions:
            print(f"\n📝 Testing question: '{question}'")
            
            # Get context
            context = await rag_system.retrieve_relevant_context(question)
            
            print(f"✅ Retrieved {len(context)} contexts")
            for i, ctx in enumerate(context[:2]):  # Show first 2 contexts
                print(f"   Context {i+1}: {ctx[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_local_vanna_with_rag():
    """Test local Vanna with improved RAG context."""
    print("\n🤖 Testing Local Vanna with RAG Context")
    print("=" * 50)
    
    try:
        # Import local Vanna client
        from app.infrastructure.local_vanna_client import LocalVannaClientRepository
        
        # Create client
        client = LocalVannaClientRepository()
        
        # Initialize
        print("🔧 Initializing local Vanna client...")
        success = await client.initialize()
        
        if not success:
            print("❌ Client initialization failed")
            return False
        
        print("✅ Client initialized successfully")
        
        # Test SQL generation
        test_question = "Show me users with their order count"
        print(f"\n📝 Testing SQL generation: '{test_question}'")
        
        # Generate SQL
        sql = await client.generate_sql(test_question)
        print(f"✅ Generated SQL: {sql}")
        
        # Check if SQL uses correct column names
        if "u.username" in sql or "username" in sql:
            print("✅ SQL uses correct column names (username)")
        elif "u.name" in sql or "name" in sql:
            print("⚠️ SQL still uses incorrect column names (name)")
        else:
            print("❓ SQL column usage unclear")
        
        return True
        
    except Exception as e:
        print(f"❌ Vanna test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🔧 Testing Improved RAG System")
    print("=" * 50)
    
    try:
        # Test RAG system
        rag_success = asyncio.run(test_improved_rag())
        
        if rag_success:
            print("\n✅ RAG system test completed successfully")
        else:
            print("\n❌ RAG system test failed")
        
        # Test local Vanna with RAG
        vanna_success = asyncio.run(test_local_vanna_with_rag())
        
        if vanna_success:
            print("\n✅ Local Vanna test completed successfully")
        else:
            print("\n❌ Local Vanna test failed")
        
        if rag_success and vanna_success:
            print("\n🎉 All tests completed successfully!")
            print("\n📝 Next steps:")
            print("1. Restart your web interface")
            print("2. Test with: 'Show me users with their order count'")
            print("3. The generated SQL should now use correct column names")
        else:
            print("\n❌ Some tests failed - check the errors above")
            
    except Exception as e:
        print(f"❌ Main test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
