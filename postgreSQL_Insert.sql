--Create a staging table
CREATE TABLE sugarprices.TempSugarPrices (
    Date VARCHAR(50),
    Nairobip MONEY,
    FX_Rate FLOAT
);

--Load data into the staging table
\copy sugarprices.TempSugarPrices FROM '/home/cliffe/Downloads/SugarQube/sugarprices.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER)

--Add a notice to report how many rows were loaded from the CSV file
DO $$
DECLARE
    rows_loaded INT;
BEGIN
    SELECT count(*) INTO rows_loaded FROM sugarprices.TempSugarPrices;
    RAISE NOTICE 'DEBUG: Loaded % rows into TempSugarPrices from CSV.', rows_loaded;
END $$;

--Insert the data into the database
MERGE INTO sugarprices.sugarprices AS target
USING (
    SELECT
        to_date(Date, 'DD/MM/YYYY') AS ConvertedDate,
        Nairobip,
        FX_Rate
    FROM sugarprices.TempSugarPrices
) AS source
ON target."Date" = source.ConvertedDate
WHEN MATCHED THEN
    UPDATE SET
        "Amount" = source.Nairobip,
        "Rate" = source.FX_Rate
WHEN NOT MATCHED BY TARGET THEN
    INSERT ("Date", "Amount", "Rate")
    VALUES (source.ConvertedDate, source.Nairobip, source.FX_Rate);

--Add a notice to report the outcome
DO $$
DECLARE
    rows_affected INT;
BEGIN
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    RAISE NOTICE 'DEBUG: The MERGE operation affected % rows (updated or inserted).', rows_affected;
END $$;

--Clean up the temp table
DROP TABLE sugarprices.TempSugarPrices;