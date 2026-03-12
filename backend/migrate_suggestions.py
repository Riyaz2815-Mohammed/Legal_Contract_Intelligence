import os
import psycopg2
from dotenv import load_dotenv

def run_migration():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return

    sql = """
    -- =============================================================
    -- CLAUSE_SUGGESTIONS
    -- Track-changes / suggestion mode for clause edits
    -- Mirrors the clauses table structure + adds suggestion fields
    -- =============================================================
    CREATE TABLE IF NOT EXISTS clause_suggestions (
        id             TEXT        PRIMARY KEY,              -- sug-XXXXXXXX
        contract_id    TEXT        NOT NULL,                 -- documents.id
        -- Mirrors clauses table
        clause_id      TEXT        NOT NULL,                 -- CLZ-XXXXXXXX
        clause         TEXT        NOT NULL,                 -- 'Confidentiality', 'Termination', etc.
        content_id     TEXT        NOT NULL,                 -- CNT-XXXXXXXX
        content        TEXT        NOT NULL,                 -- original clause text at suggestion time
        page_number    INT         NOT NULL DEFAULT 1,
        document       TEXT        NOT NULL,                 -- document_type label: NDA, MSA, SOW
        document_id    TEXT        REFERENCES documents(id) ON DELETE SET NULL,
        -- Suggestion-specific fields
        change_type    TEXT        NOT NULL                  -- 'insert' | 'delete' | 'replace'
                       CHECK (change_type IN ('insert', 'delete', 'replace')),
        original_text  TEXT        NOT NULL,                 -- text segment being removed/replaced
        suggested_text TEXT        NOT NULL DEFAULT '',      -- proposed replacement/addition
        author         TEXT        NOT NULL,                 -- user name or email
        timestamp      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        status         TEXT        NOT NULL DEFAULT 'pending'
                       CHECK (status IN ('pending', 'accepted', 'rejected'))
    );

    CREATE INDEX IF NOT EXISTS idx_suggestions_contract   ON clause_suggestions(contract_id);
    CREATE INDEX IF NOT EXISTS idx_suggestions_content_id ON clause_suggestions(content_id);
    CREATE INDEX IF NOT EXISTS idx_suggestions_status     ON clause_suggestions(status);
    """

    try:
        conn = psycopg2.connect(db_url)
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("Migration successful: clause_suggestions table created.")
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
