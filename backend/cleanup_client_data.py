"""
Cleanup script — safely removes all client documents, their extracted clauses,
review data, and local JSON files. Does NOT touch legal standard clauses or ChromaDB.

Run with: python cleanup_client_data.py --preview    (safe, shows what will be deleted)
Run with: python cleanup_client_data.py --confirm    (actually deletes)
"""
import sys
import psycopg2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from vector_pipeline.config.settings import DATABASE_URL

DATA_DIR = Path(__file__).parent / "data"


def run(dry_run=True):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("\n" + "="*60)
    print("CLIENT DATA CLEANUP" + (" [PREVIEW]" if dry_run else " [DELETING]"))
    print("="*60)

    # 1. All documents (these are all client uploads)
    cur.execute("SELECT id, filename, document_type FROM documents")
    docs = cur.fetchall()
    print(f"\n📄 Documents to delete: {len(docs)}")
    for doc_id, filename, dtype in docs:
        print(f"   - {doc_id}: {filename} ({dtype})")

    # 2. Client clauses (source='client')
    cur.execute("SELECT COUNT(*) FROM clauses WHERE source = 'client'")
    clause_count = cur.fetchone()[0]
    print(f"\n📋 Client clauses to delete: {clause_count}")

    # 3. All review records
    cur.execute("SELECT COUNT(*) FROM document_reviews")
    review_count = cur.fetchone()[0]
    print(f"\n🔍 Review records to delete: {review_count}")

    # 4. Local review JSON files
    reviews_dir = DATA_DIR / "reviews"
    json_files = list(reviews_dir.glob("*.json")) if reviews_dir.exists() else []
    print(f"\n📁 Local review JSON files to delete: {len(json_files)}")
    for f in json_files:
        print(f"   - {f.name}")

    if dry_run:
        print("\n⚠️  DRY RUN — nothing was deleted.")
        print("   Run with --confirm to permanently delete all of the above.")
        conn.close()
        return

    # === ACTUAL DELETION ===
    doc_ids = [d[0] for d in docs]

    # Delete document_reviews
    cur.execute("DELETE FROM document_reviews")
    print(f"\n✅ Deleted {review_count} review records.")

    # Delete client clauses
    cur.execute("DELETE FROM clauses WHERE source = 'client'")
    print(f"✅ Deleted {clause_count} client clauses.")

    # Delete all documents
    cur.execute("DELETE FROM documents")
    print(f"✅ Deleted {len(docs)} documents.")

    conn.commit()
    conn.close()

    # Delete local JSON files
    deleted_files = 0
    for f in json_files:
        f.unlink()
        deleted_files += 1
    print(f"✅ Deleted {deleted_files} local review JSON files.")

    print("\n🎯 Cleanup complete!")
    print("   Legal standard clauses (source='legal') and ChromaDB are UNTOUCHED.")


if __name__ == "__main__":
    if "--confirm" in sys.argv:
        run(dry_run=False)
    else:
        run(dry_run=True)
