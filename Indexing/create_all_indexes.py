"""
Main script to create all indexes
Runs both needle and summary indexing systems
"""

import sys

# Handle imports for both module execution and direct script execution
try:
    from Indexing.needle_indexing import create_needle_index
    from Indexing.summary_indexing import create_summary_index
except ModuleNotFoundError:
    from needle_indexing import create_needle_index
    from summary_indexing import create_summary_index


def main():
    """Create all indexes in sequence"""
    print("\n" + "=" * 70)
    print("INSURANCE CLAIM INDEXING SYSTEM")
    print("Creating all indexes...")
    print("=" * 70 + "\n")
    
    try:
        # Step 0: Setup database tables
        print("\n" + "="*70)
        print("STEP 0: DATABASE SETUP")
        print("="*70)
        print("\nPreparing database tables for indexing...")
        print("This will drop and recreate tables to ensure clean schema.")
        print("-" * 70)
        
        try:
            from Indexing.supabase_setup import ensure_tables_exist
        except ModuleNotFoundError:
            from supabase_setup import ensure_tables_exist
        
        if not ensure_tables_exist(force_recreate=True):
            print("\n" + "="*70)
            print("[ABORTED] Database setup failed.")
            print("="*70)
            print("\nPlease check:")
            print("  - Your Supabase credentials in .env file")
            print("  - Your internet connection")
            print("  - Your Supabase project is accessible")
            return None, None
        
        print("="*70)
        print("DATABASE SETUP COMPLETE - Proceeding with indexing...")
        print("="*70)
        
        # Step 1: Create needle index
        print("\n[STEP 1/2] Creating Needle Index...")
        print("-" * 70)
        needle_index, docstore = create_needle_index()
        
        if needle_index is None:
            print("\n[ABORTED] Needle index creation failed.")
            return None, None
        
        print("\n[OK] Needle index created successfully!")
        
        # Step 2: Create summary index
        print("\n[STEP 2/2] Creating Summary Index...")
        print("-" * 70)
        summary_index = create_summary_index()
        
        if summary_index is None:
            print("\n[ABORTED] Summary index creation failed.")
            return None, None
        
        print("\n[OK] Summary index created successfully!")
        
        # Final summary
        print("\n" + "=" * 70)
        print("ALL INDEXES CREATED SUCCESSFULLY!")
        print("=" * 70)
        print("\n[OK] Needle Index:")
        print("  - Small chunks (300 chars) in Supabase vector store")
        print("  - Parent pages in local document store")
        print("  - Ready for auto-merging retrieval")
        print("\n[OK] Summary Index:")
        print("  - Page summaries in Supabase vector store")
        print("  - Ready for high-level queries")
        print("\n==> System Ready:")
        print("  - You can now ask questions (Main Menu Option 1)")
        print("  - Or run RAGAS evaluation (Main Menu Option 3)")
        print("=" * 70 + "\n")
        
        return needle_index, summary_index
        
    except Exception as e:
        print(f"\n[ERROR] Error during index creation: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 70)
        print("[FAILED] Index creation did not complete successfully")
        print("=" * 70)
        return None, None


if __name__ == "__main__":
    main()

