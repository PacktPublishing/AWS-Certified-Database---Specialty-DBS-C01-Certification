CREATE PROCEDURE Northwind_dbo.`Ten Most Expensive Products`() 

SQL SECURITY DEFINER 

BEGIN 

        SELECT 

            Products.ProductName AS TenMostExpensiveProducts, Products.UnitPrice 

            FROM Products 

            ORDER BY Products.UnitPrice DESC 

LIMIT 10; 

END; 

