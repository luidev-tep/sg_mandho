-- =============================================================================
-- V3__harden_revenue_and_utc_defaults.sql
-- Endurece FACT_Revenue (amount >= 0) y corrige defaults de timestamp a SYSUTCDATETIME()
-- en bases existentes (baselined en V1) e instalaciones limpias de forma idempotente.
-- =============================================================================

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = N'CK_FACT_Revenue_Amount_NonNegative'
      AND parent_object_id = OBJECT_ID(N'dbo.FACT_Revenue')
)
BEGIN
    ALTER TABLE dbo.FACT_Revenue
    WITH NOCHECK ADD CONSTRAINT CK_FACT_Revenue_Amount_NonNegative CHECK (amount >= 0);
END;
GO

DECLARE @tableName SYSNAME;
DECLARE @constraintName SYSNAME;
DECLARE @sql NVARCHAR(MAX);

DECLARE ts_cursor CURSOR LOCAL FAST_FORWARD FOR
    SELECT
        t.name AS TableName,
        dc.name AS ConstraintName
    FROM sys.default_constraints AS dc
    INNER JOIN sys.columns AS c
        ON dc.parent_object_id = c.object_id
       AND dc.parent_column_id = c.column_id
    INNER JOIN sys.tables AS t
        ON dc.parent_object_id = t.object_id
    WHERE c.name = N'timestamp'
      AND dc.[definition] LIKE N'%sysdatetime()%'
      AND dc.[definition] NOT LIKE N'%sysutcdatetime()%';

OPEN ts_cursor;
FETCH NEXT FROM ts_cursor INTO @tableName, @constraintName;

WHILE @@FETCH_STATUS = 0
BEGIN
    SET @sql = N'ALTER TABLE dbo.' + QUOTENAME(@tableName) +
               N' DROP CONSTRAINT ' + QUOTENAME(@constraintName) + N';';
    EXEC sp_executesql @sql;

    SET @sql = N'ALTER TABLE dbo.' + QUOTENAME(@tableName) +
               N' ADD CONSTRAINT ' + QUOTENAME(@constraintName) +
               N' DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE ''UTC'' AT TIME ZONE ''Central Standard Time (Mexico)'', 120) FOR [timestamp];';
    EXEC sp_executesql @sql;

    FETCH NEXT FROM ts_cursor INTO @tableName, @constraintName;
END;

CLOSE ts_cursor;
DEALLOCATE ts_cursor;
GO
