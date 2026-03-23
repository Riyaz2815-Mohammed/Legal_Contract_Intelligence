-- ================================================================
-- LACCIS – Neon DB Setup Script
-- Paste this entire file into the Neon SQL Editor and run it.
-- Matches the exact live Supabase schema (introspected 2026-03-20)
-- ================================================================

-- ── 1. Extensions ─────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";       -- pgvector for clause_embeddings

-- ── 2. Sequence for clause_embeddings.id ──────────────────────
CREATE SEQUENCE IF NOT EXISTS clause_embeddings_id_seq;


-- ================================================================
-- USERS  (no FK deps — create first)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.users (
  id              text        NOT NULL,
  name            text        NOT NULL,
  email           text        NOT NULL,
  password_hash   text        NOT NULL,
  role            text        NOT NULL CHECK (role = ANY (ARRAY['admin'::text, 'legal_team'::text, 'client'::text])),
  created_at      timestamptz NOT NULL DEFAULT now(),
  nda_accepted    boolean     NOT NULL DEFAULT false,
  nda_accepted_at timestamptz,
  nda_rejected    boolean     DEFAULT false,
  CONSTRAINT users_pkey    PRIMARY KEY (id),
  CONSTRAINT users_email_key UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON public.users(role);


-- ================================================================
-- DOCUMENTS  (depends on users)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.documents (
  id                  text        NOT NULL,
  filename            text        NOT NULL,
  document_type       text        NOT NULL,
  user_id             text        NOT NULL,
  user_email          text        NOT NULL,
  user_role           text        NOT NULL,
  size                bigint      DEFAULT 0,
  status              text        NOT NULL DEFAULT 'uploaded'::text
                      CHECK (status = ANY (ARRAY['pending'::text, 'uploaded'::text, 'approved'::text, 'rejected'::text, 'completed'::text])),
  shared_with         jsonb       NOT NULL DEFAULT '[]'::jsonb,
  uploaded_at         timestamptz NOT NULL DEFAULT now(),
  file_path           text,
  s3_url              text,
  s3_key              text,
  template_type       text,
  approved_at         timestamptz,
  approved_by         text,
  rejected_at         timestamptz,
  rejected_by         text,
  is_finalized        boolean     NOT NULL DEFAULT false,
  google_doc_id       text        UNIQUE,
  client_marked_final boolean     NOT NULL DEFAULT false,
  CONSTRAINT documents_pkey          PRIMARY KEY (id),
  CONSTRAINT documents_user_id_fkey  FOREIGN KEY (user_id)      REFERENCES public.users(id) ON DELETE CASCADE,
  CONSTRAINT documents_approved_by_fkey  FOREIGN KEY (approved_by)  REFERENCES public.users(id),
  CONSTRAINT documents_rejected_by_fkey  FOREIGN KEY (rejected_by)  REFERENCES public.users(id)
);

CREATE INDEX IF NOT EXISTS idx_documents_user_id       ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status        ON public.documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON public.documents(document_type);


-- ================================================================
-- CLAUSES  (depends on documents)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.clauses (
  clause_id       text        NOT NULL,
  clause          text        NOT NULL,
  content_id      text        NOT NULL,
  content         text        NOT NULL,
  page_number     integer     NOT NULL DEFAULT 1,
  document        text        NOT NULL,
  source          text        NOT NULL CHECK (source = ANY (ARRAY['client'::text, 'legal'::text, 'unknown'::text])),
  document_id     text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  approval_status varchar     DEFAULT 'pending'::character varying,
  edited_content  text,
  comment         text,
  CONSTRAINT clauses_pkey              PRIMARY KEY (clause_id),
  CONSTRAINT clauses_content_id_key    UNIQUE (content_id),
  CONSTRAINT clauses_document_id_fkey  FOREIGN KEY (document_id) REFERENCES public.documents(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_clauses_document_id ON public.clauses(document_id);
CREATE INDEX IF NOT EXISTS idx_clauses_clause      ON public.clauses(clause);


-- ================================================================
-- DOCUMENT_REVIEWS  (depends on documents)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.document_reviews (
  document_id text    NOT NULL,
  review_data jsonb   NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT document_reviews_pkey           PRIMARY KEY (document_id),
  CONSTRAINT document_reviews_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id) ON DELETE CASCADE
);


-- ================================================================
-- EDITED_CLAUSES  (depends on clauses)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.edited_clauses (
  content_id      text        NOT NULL,
  original_clause text        NOT NULL,
  edited_clause   text,
  comment         text,
  updated_at      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT edited_clauses_pkey            PRIMARY KEY (content_id),
  CONSTRAINT edited_clauses_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.clauses(content_id) ON DELETE CASCADE
);


-- ================================================================
-- MESSAGES  (depends on users)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.messages (
  id           text        NOT NULL,
  sender_id    text        NOT NULL,
  recipient_id text        NOT NULL,
  content      text        NOT NULL,
  timestamp    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT messages_pkey             PRIMARY KEY (id),
  CONSTRAINT messages_sender_id_fkey   FOREIGN KEY (sender_id)    REFERENCES public.users(id) ON DELETE CASCADE,
  CONSTRAINT messages_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_sender    ON public.messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient ON public.messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_convo     ON public.messages(
    LEAST(sender_id, recipient_id),
    GREATEST(sender_id, recipient_id)
);


-- ================================================================
-- SHARED_CONTRACTS  (depends on users)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.shared_contracts (
  id              text        NOT NULL,
  filename        text        NOT NULL,
  document_type   text,
  client_id       text        NOT NULL,
  shared_by       text        NOT NULL,
  shared_by_email text        NOT NULL,
  message         text,
  size            bigint      DEFAULT 0,
  status          text        NOT NULL DEFAULT 'pending_review'::text
                  CHECK (status = ANY (ARRAY['pending_review'::text, 'accepted'::text, 'rejected'::text])),
  shared_at       timestamptz NOT NULL DEFAULT now(),
  accepted_at     timestamptz,
  file_path       text,
  s3_key          text,
  s3_url          text,
  is_finalized    boolean     NOT NULL DEFAULT false,
  CONSTRAINT shared_contracts_pkey           PRIMARY KEY (id),
  CONSTRAINT shared_contracts_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id) ON DELETE CASCADE,
  CONSTRAINT shared_contracts_shared_by_fkey FOREIGN KEY (shared_by) REFERENCES public.users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_shared_contracts_client_id ON public.shared_contracts(client_id);
CREATE INDEX IF NOT EXISTS idx_shared_contracts_shared_by ON public.shared_contracts(shared_by);
CREATE INDEX IF NOT EXISTS idx_shared_contracts_status    ON public.shared_contracts(status);


-- ================================================================
-- ACTIVITY_LOG  (depends on users)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.activity_log (
  id        text        NOT NULL,
  user_id   text        NOT NULL,
  client_id text,
  action    text        NOT NULL,
  details   text        DEFAULT ''::text,
  timestamp timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT activity_log_pkey         PRIMARY KEY (id),
  CONSTRAINT activity_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_activity_user_id   ON public.activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_client_id ON public.activity_log(client_id);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON public.activity_log(timestamp DESC);


-- ================================================================
-- CLAUSE_SUGGESTIONS  (depends on documents)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.clause_suggestions (
  id             text        NOT NULL,
  clause_id      text        NOT NULL,
  clause         text        NOT NULL,
  content_id     text        NOT NULL,
  content        text        NOT NULL,
  page_number    integer     NOT NULL DEFAULT 1,
  document       text        NOT NULL,
  document_id    text,
  change_type    text        NOT NULL CHECK (change_type = ANY (ARRAY['insert'::text, 'delete'::text, 'replace'::text])),
  original_text  text        NOT NULL,
  suggested_text text        NOT NULL DEFAULT ''::text,
  author         text        NOT NULL,
  timestamp      timestamptz NOT NULL DEFAULT now(),
  status         text        NOT NULL DEFAULT 'pending'::text CHECK (status = ANY (ARRAY['pending'::text, 'accepted'::text, 'rejected'::text])),
  CONSTRAINT clause_suggestions_pkey              PRIMARY KEY (id),
  CONSTRAINT clause_suggestions_document_id_fkey  FOREIGN KEY (document_id) REFERENCES public.documents(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_suggestions_document_id ON public.clause_suggestions(document_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_content_id  ON public.clause_suggestions(content_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_status      ON public.clause_suggestions(status);


-- ================================================================
-- CLAUSE_EMBEDDINGS  (pgvector — no FK deps, standalone)
-- ================================================================
CREATE TABLE IF NOT EXISTS public.clause_embeddings (
  id          integer     NOT NULL DEFAULT nextval('clause_embeddings_id_seq'::regclass),
  clause_id   text        NOT NULL,
  clause      text        NOT NULL,
  content_id  text        NOT NULL,
  content     text        NOT NULL,
  embedding   vector(384),           -- all-MiniLM-L6-v2 produces 384-dim vectors
  document    text,
  document_id text,
  created_at  timestamptz DEFAULT now(),
  page_number integer,
  CONSTRAINT clause_embeddings_pkey        PRIMARY KEY (id),
  CONSTRAINT clause_embeddings_content_id_key UNIQUE (content_id)
);

CREATE INDEX IF NOT EXISTS idx_clause_embeddings_clause     ON public.clause_embeddings(clause);
CREATE INDEX IF NOT EXISTS idx_clause_embeddings_content_id ON public.clause_embeddings(content_id);


-- ================================================================
-- SEED: Default admin user
-- WARNING: password is plaintext — replace with bcrypt in prod
-- ================================================================
INSERT INTO public.users (id, name, email, password_hash, role, nda_accepted, nda_rejected, created_at)
VALUES (
    'admin-1',
    'Legal Team Admin',
    'admin@laccis.com',
    'admin123',
    'admin',
    false,
    false,
    now()
)
ON CONFLICT (email) DO NOTHING;