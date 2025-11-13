-- reputation scores correspond to the guide.txt in backend-functions
-- notes throughout to enable more data for potential LLM analysis
CREATE TABLE IF NOT EXISTS domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,
    reputation_score INTEGER DEFAULT 2,
    notes TEXT
);

-- foreign key in the domains to quickly filter out wider ranges of emails
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    domain_id INTEGER,
    reputation_score INTEGER DEFAULT 2,
    FOREIGN KEY(domain_id) REFERENCES domains(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS suspicious_phrases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase TEXT NOT NULL,
    notes TEXT
);

-- foreign key in the domains to quickly filter out wider ranges of links
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    domain_id INTEGER,
    reputation_score INTEGER DEFAULT 2,
    notes TEXT,
    FOREIGN KEY(domain_id) REFERENCES domains(id) ON DELETE SET NULL
);
