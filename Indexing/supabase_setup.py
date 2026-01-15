"""
Supabase Database Setup
Automatically creates required tables if they don't exist
"""

from supabase import create_client, Client
from Config import config
import re


def create_tables_automatically():
    """
    Automatically create tables using PostgreSQL connection
    Returns True if successful, False otherwise
    """
    try:
        import psycopg2
    except ImportError:
        print("\n✗ psycopg2 not installed. Installing required package...")
        print("Run: pip install psycopg2-binary")
        return False
    
    try:
        # Extract database connection details from Supabase URL
        # Format: https://xxxx.supabase.co
        match = re.search(r'https://([^.]+)\.supabase\.co', config.SUPABASE_URL)
        if not match:
            print("✗ Could not parse Supabase URL")
            return False
        
        project_id = match.group(1)
        db_host = f"db.{project_id}.supabase.co"
        
        print(f"Connecting to PostgreSQL at {db_host}...")
        
        # Connect to Supabase PostgreSQL database
        conn = psycopg2.connect(
            host=db_host,
            port=5432,
            database="postgres",
            user="postgres",
            password=config.SUPABASE_DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Enable vector extension
        print("Enabling vector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Drop existing tables to ensure clean schema (recreate if they exist)
        print("Checking for existing tables...")
        cursor.execute(f"DROP TABLE IF EXISTS {config.CHUNKS_TABLE};")
        cursor.execute(f"DROP TABLE IF EXISTS {config.SUMMARIES_TABLE};")
        print("Creating fresh tables with correct schema...")
        
        # Create claim_chunks table
        print(f"Creating table '{config.CHUNKS_TABLE}'...")
        cursor.execute(f"""
            CREATE TABLE {config.CHUNKS_TABLE} (
                chunk_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding VECTOR(1536),
                metadata JSONB,
                page_number INTEGER,
                chunk_index INTEGER,
                parent_id TEXT
            );
        """)
        
        # Create claim_summaries table
        print(f"Creating table '{config.SUMMARIES_TABLE}'...")
        cursor.execute(f"""
            CREATE TABLE {config.SUMMARIES_TABLE} (
                summary_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding VECTOR(1536),
                metadata JSONB,
                page_number INTEGER,
                summary_type TEXT
            );
        """)
        
        # Grant permissions for Supabase PostgREST API
        print("Setting up permissions...")
        cursor.execute(f"""
            GRANT ALL ON TABLE {config.CHUNKS_TABLE} TO postgres, anon, authenticated, service_role;
            GRANT ALL ON TABLE {config.SUMMARIES_TABLE} TO postgres, anon, authenticated, service_role;
        """)
        
        # Reload PostgREST schema cache to immediately recognize new tables
        print("Reloading schema cache...")
        try:
            cursor.execute("NOTIFY pgrst, 'reload schema';")
        except Exception as e:
            print(f"Note: Could not reload schema cache ({e}), but tables are created.")
        
        # Commit changes
        conn.commit()
        
        # Verify tables exist using PostgreSQL
        print("Verifying tables in database...")
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{config.CHUNKS_TABLE}'
            );
        """)
        chunks_exists = cursor.fetchone()[0]
        
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{config.SUMMARIES_TABLE}'
            );
        """)
        summaries_exists = cursor.fetchone()[0]
        
        if chunks_exists and summaries_exists:
            print("✓ Tables created and verified successfully!")
            print("\n⏳ Waiting for Supabase REST API to recognize new tables...")
            print("   (This is a one-time delay to ensure schema cache is updated)")
            import time
            for i in range(20, 0, -1):
                print(f"   Waiting {i} seconds...    ", end='\r')
                time.sleep(1)
            print("\n")
            
            # Verify one more time after waiting
            print("Verifying tables are accessible...")
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('{config.CHUNKS_TABLE}', '{config.SUMMARIES_TABLE}');
            """)
            table_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if table_count == 2:
                print("✓ Both tables confirmed ready")
                print("✓ Ready to proceed with indexing\n")
                return True
            else:
                print("✗ Tables verification failed after wait")
                return False
        else:
            print("✗ Table creation verification failed")
            cursor.close()
            conn.close()
            return False
        
    except Exception as e:
        print(f"✗ Error creating tables automatically: {e}")
        return False


def ensure_tables_exist(force_recreate=True):
    """
    Create Supabase tables if they don't exist.
    
    Args:
        force_recreate: If True, drops and recreates tables even if they exist.
                       This ensures fresh schema and clean data for indexing.
    """
    print("\n" + "="*60)
    print("Checking Supabase database setup...")
    print("="*60)
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        
        # SQL to create tables if they don't exist
        create_tables_sql = """
        -- Enable vector extension
        CREATE EXTENSION IF NOT EXISTS vector;

        -- Create claim_chunks table
        CREATE TABLE IF NOT EXISTS claim_chunks (
            chunk_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            embedding VECTOR(1536),
            metadata JSONB,
            page_number INTEGER,
            chunk_index INTEGER,
            parent_id TEXT
        );

        -- Create claim_summaries table
        CREATE TABLE IF NOT EXISTS claim_summaries (
            summary_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            embedding VECTOR(1536),
            metadata JSONB,
            page_number INTEGER,
            summary_type TEXT
        );
        """
        
        # Check if tables exist using PostgreSQL directly (more reliable than REST API)
        tables_exist = False
        try:
            import psycopg2
            match = re.search(r'https://([^.]+)\.supabase\.co', config.SUPABASE_URL)
            if match:
                project_id = match.group(1)
                db_host = f"db.{project_id}.supabase.co"
                
                conn = psycopg2.connect(
                    host=db_host,
                    port=5432,
                    database="postgres",
                    user="postgres",
                    password=config.SUPABASE_DB_PASSWORD
                )
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = '{config.CHUNKS_TABLE}'
                    );
                """)
                chunks_exists = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = '{config.SUMMARIES_TABLE}'
                    );
                """)
                summaries_exists = cursor.fetchone()[0]
                
                cursor.close()
                conn.close()
                
                tables_exist = chunks_exists and summaries_exists
                
                if chunks_exists:
                    print(f"✓ Table '{config.CHUNKS_TABLE}' exists")
                else:
                    print(f"✗ Table '{config.CHUNKS_TABLE}' does not exist")
                    
                if summaries_exists:
                    print(f"✓ Table '{config.SUMMARIES_TABLE}' exists")
                else:
                    print(f"✗ Table '{config.SUMMARIES_TABLE}' does not exist")
        except Exception as e:
            # Fallback to REST API check if PostgreSQL check fails
            print(f"Note: Direct database check unavailable ({str(e)[:50]}...)")
            print("Falling back to REST API check...")
            tables_exist = True
            try:
                supabase.table(config.CHUNKS_TABLE).select("chunk_id").limit(1).execute()
                print(f"✓ Table '{config.CHUNKS_TABLE}' exists")
            except Exception:
                tables_exist = False
                print(f"✗ Table '{config.CHUNKS_TABLE}' does not exist")
            
            try:
                supabase.table(config.SUMMARIES_TABLE).select("summary_id").limit(1).execute()
                print(f"✓ Table '{config.SUMMARIES_TABLE}' exists")
            except Exception:
                tables_exist = False
                print(f"✗ Table '{config.SUMMARIES_TABLE}' does not exist")
        
        if force_recreate or not tables_exist:
            if force_recreate and tables_exist:
                print("\n⚠ Recreating tables with fresh schema...")
            else:
                print("\n⚠ Database tables not found. Creating new tables...")
            
            # Try to create tables automatically (drops existing if force_recreate=True)
            if create_tables_automatically():
                return True  # Already includes wait time and success message
            else:
                # Automatic creation failed, show manual instructions
                print("\n" + "="*60)
                print("⚠ MANUAL DATABASE SETUP REQUIRED ⚠")
                print("="*60)
                print("\nAutomatic setup failed. Please run the following SQL manually:")
                print("\n" + "-"*60)
                print(create_tables_sql)
                print("-"*60)
                print("\nInstructions:")
                print("1. Copy the SQL above (use mouse to select)")
                print("2. Go to your Supabase project → SQL Editor")
                print("3. Paste and run the SQL")
                print("4. Come back here and press Enter to continue")
                print("="*60)
                
                try:
                    input("\nPress Enter after you've created the tables (or Ctrl+C to exit)...")
                except KeyboardInterrupt:
                    print("\n\n[ABORTED] Indexing cancelled.")
                    return False
                
                # Verify tables exist now by checking again
                print("\nVerifying tables...")
                try:
                    supabase.table(config.CHUNKS_TABLE).select("chunk_id").limit(1).execute()
                    supabase.table(config.SUMMARIES_TABLE).select("summary_id").limit(1).execute()
                    print(f"✓ Table '{config.CHUNKS_TABLE}' verified")
                    print(f"✓ Table '{config.SUMMARIES_TABLE}' verified")
                    print("\n✓ All required tables exist and are accessible")
                    print("="*60 + "\n")
                    return True
                except Exception as e:
                    print(f"\n✗ Tables still not accessible: {e}")
                    print("\nPlease check and try running the indexing again.")
                    return False
        else:
            print("\n✓ All required tables exist and are accessible")
            print("="*60 + "\n")
            return True
            
    except Exception as e:
        print(f"\n✗ Error connecting to Supabase: {e}")
        print("\nPlease check your Supabase credentials in the .env file:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")
        return False


if __name__ == "__main__":
    ensure_tables_exist()

