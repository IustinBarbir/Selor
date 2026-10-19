-- =====================================================================
-- SELOR - selling_partner_cases table schema
-- =====================================================================

CREATE TABLE IF NOT EXISTS selling_partner_cases (
    id                     INT AUTO_INCREMENT PRIMARY KEY,

    case_type              ENUM('DR', 'SA') NOT NULL,
    case_id                VARCHAR(50)  NOT NULL,

    sp_type                ENUM('Vendor', 'Seller', 'N/A') NOT NULL,

    sp_identifier          VARCHAR(100) NULL,
    sp_identifier_na       TINYINT(1)   NOT NULL DEFAULT 0,

    seller_business_model  ENUM('FBA', 'MFN', 'N/A') NOT NULL,

    -- SP name
    sp_name                VARCHAR(255) NULL,
    sp_name_na             TINYINT(1)   NOT NULL DEFAULT 0,

    asin                   VARCHAR(20)  NULL,
    asin_na                TINYINT(1)   NOT NULL DEFAULT 0,

    marketplace            ENUM('UK', 'DE', 'FR', 'IT', 'ES', 'N/A') NOT NULL,

    case_status             ENUM('Approved', 'Not Approved', 'Other', 'Pending Review') NOT NULL,

    case_reason_code        VARCHAR(100) NOT NULL,

    expiry_date              DATE NULL,
    expiry_na                TINYINT(1)   NOT NULL DEFAULT 0,

    -- The date the case was actually worked.
    case_date                DATE NULL,

    -- Free-text notes
    notes                   VARCHAR(255) NULL,

    uploader                VARCHAR(100) NOT NULL,
    upload_date              DATETIME     NOT NULL,

    INDEX idx_case_id       (case_id),
    INDEX idx_sp_identifier (sp_identifier),
    INDEX idx_asin          (asin),
    INDEX idx_expiry        (expiry_date),
    INDEX idx_case_date     (case_date),
    INDEX idx_status        (case_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- MIGRATION: if your table already exists and lacks case_date, run:
-- =====================================================================
-- ALTER TABLE selling_partner_cases ADD COLUMN case_date DATE NULL AFTER expiry_na;
-- ALTER TABLE selling_partner_cases ADD INDEX idx_case_date (case_date);

-- =====================================================================
-- Least-privilege application account (recommended)
-- =====================================================================
-- CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'CHANGE_ME';
-- GRANT SELECT, INSERT ON <database_name>.selling_partner_cases TO 'app_user'@'%';
-- FLUSH PRIVILEGES;
