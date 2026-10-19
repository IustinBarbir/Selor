-- =============================================================================
--  SELOR - Query-uri pentru MODIFICARE DATE in MySQL Workbench
-- =============================================================================
--  Cum se folosesc:
--    1. Copiaza query-ul dorit intr-un tab nou in Workbench
--    2. Inlocuieste textul dintre [ ] cu valorile tale (sterge si parantezele)
--    3. Ruleaza INTAI query-ul de verificare (Pasul 1) sa vezi ce modifici
--    4. Decoment-eaza si ruleaza query-ul de modificare (Pasul 2)
--
--  IMPORTANT: Valorile text se pun intre ghilimele simple: 'valoare'
--             Datele se scriu in format: 'YYYY-MM-DD'  (ex: '2026-10-15')
--             [ID] este numarul din prima coloana cand cauti un caz in app
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- 1. MODIFICA ASIN-ul UNUI CAZ
--    [ID]        = numarul din coloana ID
--    [ASIN_NOU]  = noul ASIN (ex: B0BGF8RDQ7)
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, asin, sp_identifier, marketplace FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica (decoment-eaza linia de mai jos)
-- UPDATE selling_partner_cases SET asin = '[ASIN_NOU]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 2. MODIFICA CASE ID
--    [ID]           = numarul din coloana ID
--    [CASE_ID_NOU]  = noul Case ID
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, asin, sp_identifier, marketplace FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica
-- UPDATE selling_partner_cases SET case_id = '[CASE_ID_NOU]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 3. MODIFICA SELLING PARTNER ID / VENDOR CODE
--    [ID]      = numarul din coloana ID
--    [SP_NOU]  = noul Selling Partner ID (ex: 311504208112)
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, sp_identifier, sp_name, marketplace FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica
-- UPDATE selling_partner_cases SET sp_identifier = '[SP_NOU]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 4. MODIFICA STATUSUL UNUI CAZ
--    [ID]          = numarul din coloana ID
--    [STATUS_NOU]  = Approved / Not Approved / Other / Pending Review
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, case_status, case_reason_code FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica
-- UPDATE selling_partner_cases SET case_status = '[STATUS_NOU]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 5. MODIFICA REASON CODE
--    [ID]          = numarul din coloana ID
--    [REASON_NOU]  = noul reason code (ex: Correct First Submission)
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, case_status, case_reason_code FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica
-- UPDATE selling_partner_cases SET case_reason_code = '[REASON_NOU]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 6. MODIFICA EXPIRY DATE
--    [ID]        = numarul din coloana ID
--    [DATA_NOUA] = noua data de expirare (ex: 2027-06-15)
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, expiry_date, expiry_na FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica (seteaza si expiry_na = 0 ca sa nu ramana marcat ca N/A)
-- UPDATE selling_partner_cases SET expiry_date = '[DATA_NOUA]', expiry_na = 0 WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 7. MODIFICA CASE DATE (data cand s-a lucrat cazul)
--    [ID]        = numarul din coloana ID
--    [DATA_NOUA] = noua data (ex: 2026-10-07)
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, case_date, uploader FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica
-- UPDATE selling_partner_cases SET case_date = '[DATA_NOUA]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 8. MODIFICA MARKETPLACE
--    [ID]     = numarul din coloana ID
--    [MP_NOU] = UK / DE / FR / IT / ES / N/A
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, marketplace, sp_identifier FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica
-- UPDATE selling_partner_cases SET marketplace = '[MP_NOU]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 9. MODIFICA CASE TYPE (DR / SA)
--    [ID]       = numarul din coloana ID
--    [TIP_NOU]  = DR sau SA
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, case_type, asin, sp_name FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica
-- UPDATE selling_partner_cases SET case_type = '[TIP_NOU]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 10. MODIFICA BUSINESS MODEL
--     [ID]          = numarul din coloana ID
--     [MODEL_NOU]   = FBA / MFN / N/A
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul
SELECT id, case_id, seller_business_model, sp_identifier FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica
-- UPDATE selling_partner_cases SET seller_business_model = '[MODEL_NOU]' WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 11. MODIFICA MAI MULTE CAMPURI ODATA
--     Pune doar campurile pe care vrei sa le schimbi, sterge restul
--     [ID] = numarul din coloana ID
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: vezi tot randul
SELECT * FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: modifica (pastreaza doar liniile care te intereseaza, sterge restul)
-- UPDATE selling_partner_cases
-- SET
--     case_id = '[CASE_ID_NOU]',
--     asin = '[ASIN_NOU]',
--     sp_identifier = '[SP_NOU]',
--     marketplace = '[MP_NOU]',
--     case_status = '[STATUS_NOU]',
--     case_reason_code = '[REASON_NOU]',
--     expiry_date = '[DATA_NOUA]',
--     case_date = '[DATA_NOUA]'
-- WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 12. STERGE UN RAND
--     [ID] = numarul din coloana ID
--     ATENTIE: Stergerea este IREVERSIBILA!
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: verifica randul (OBLIGATORIU inainte de stergere!)
SELECT * FROM selling_partner_cases WHERE id = [ID];

-- Pasul 2: sterge
-- DELETE FROM selling_partner_cases WHERE id = [ID];


-- ─────────────────────────────────────────────────────────────────────────────
-- 13. STERGE TOATE CAZURILE UPLOADATE DE UN USER INTR-O ZI
--     (util daca cineva a importat date gresite)
--     [USERNAME] = userul care a uploadat (ex: john_doe)
--     [DATA]     = data upload-ului (ex: 2026-10-07)
-- ─────────────────────────────────────────────────────────────────────────────

-- Pasul 1: vezi cate randuri ar fi sterse
SELECT COUNT(*) AS randuri_afectate
FROM selling_partner_cases
WHERE uploader = '[USERNAME]' AND DATE(upload_date) = '[DATA]';

-- Pasul 2: vezi randurile
SELECT id, case_id, asin, sp_identifier, upload_date
FROM selling_partner_cases
WHERE uploader = '[USERNAME]' AND DATE(upload_date) = '[DATA]';

-- Pasul 3: sterge (doar dupa ce ai verificat la Pasul 1 si 2!)
-- DELETE FROM selling_partner_cases WHERE uploader = '[USERNAME]' AND DATE(upload_date) = '[DATA]';
