// Morrowfield Food Co. | Power Query transformation reference
// In Power BI Desktop create a text parameter called PortfolioFolder that points
// to the extracted project root. Then create individual queries from the blocks
// below. No user-specific machine path is embedded in the project.

// Query: fxLoadCsv
(FileName as text) as table =>
let
    Source = Csv.Document(
        File.Contents(PortfolioFolder & "/data/raw/" & FileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    PromotedHeaders

// Query: DimStores
let
    Source = fxLoadCsv("DimStores.csv"),
    TrimmedKeys = Table.TransformColumns(Source, {{"StoreID", Text.Trim, type text}, {"StoreName", Text.Trim, type text}, {"Region", Text.Trim, type text}}),
    NormalisedRegion = Table.ReplaceValue(
        TrimmedKeys,
        each [Region],
        each if [Region] = "GAUTENG" then "Gauteng"
             else if [Region] = "Western cape" then "Western Cape"
             else if [Region] = "KZN" then "KwaZulu-Natal"
             else if [Region] = "Eastern-Cape" then "Eastern Cape"
             else [Region],
        Replacer.ReplaceValue,
        {"Region"}
    ),
    Typed = Table.TransformColumnTypes(NormalisedRegion, {{"SellingAreaSqm", Int64.Type}, {"CommercialIndex", type number}, {"OperatingSince", type date}})
in
    Typed

// Query: DimProducts
let
    Source = fxLoadCsv("DimProducts.csv"),
    Trimmed = Table.TransformColumns(Source, {{"ProductID", Text.Trim, type text}, {"ProductName", Text.Trim, type text}, {"Category", Text.Trim, type text}}),
    Deduplicated = Table.Distinct(Trimmed, {"ProductID"}),
    CanonicalCategories = Table.TransformColumns(Deduplicated, {{"Category", each
        if Text.Lower(_) = "pantry staples" then "Pantry Staples"
        else if Text.Lower(_) = "chilled dairy" then "Chilled Dairy"
        else if Text.Lower(_) = "break fast" then "Breakfast"
        else if Text.Lower(_) = "home care" then "Household Care"
        else if Text.Lower(_) = "personal-care" then "Personal Care"
        else if Text.Lower(_) = "snacks and drinks" then "Snacks & Drinks"
        else _, type text}}),
    // Recover three missing supplier IDs using the reviewed clean mapping.
    ApprovedMappings = Csv.Document(File.Contents(PortfolioFolder & "/data/clean/DimProducts.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    MappingHeaders = Table.PromoteHeaders(ApprovedMappings, [PromoteAllScalars = true]),
    JoinedMappings = Table.NestedJoin(CanonicalCategories, {"ProductID"}, Table.SelectColumns(MappingHeaders, {"ProductID", "SupplierID"}), {"ProductID"}, "ApprovedSupplier", JoinKind.LeftOuter),
    ExpandedMappings = Table.ExpandTableColumn(JoinedMappings, "ApprovedSupplier", {"SupplierID"}, {"ApprovedSupplierID"}),
    RecoveredSupplier = Table.AddColumn(ExpandedMappings, "ResolvedSupplierID", each if [SupplierID] = null or Text.Trim([SupplierID]) = "" then [ApprovedSupplierID] else [SupplierID], type text),
    RemovedOldColumns = Table.RemoveColumns(RecoveredSupplier, {"SupplierID", "ApprovedSupplierID"}),
    RenamedSupplier = Table.RenameColumns(RemovedOldColumns, {{"ResolvedSupplierID", "SupplierID"}}),
    Typed = Table.TransformColumnTypes(RenamedSupplier, {{"ListUnitPrice", Currency.Type}, {"StandardUnitCost", Currency.Type}, {"DemandWeight", type number}, {"InventoryTracked", type logical}})
in
    Typed

// Query: FactSalesWeekly
let
    Source = fxLoadCsv("FactSalesWeekly.csv"),
    Deduplicated = Table.Distinct(Source, {"SalesRecordID"}),
    TrimmedKeys = Table.TransformColumns(Deduplicated, {{"StoreID", Text.Trim, type text}, {"ProductID", Text.Trim, type text}}),
    ParsedDates = Table.TransformColumns(TrimmedKeys, {{"WeekStartDate", each if Text.Contains(_, "/") then Date.FromText(_, [Culture = "en-ZA"]) else Date.FromText(_, [Culture = "en-CA"]), type date}}),
    ParsedDiscount = Table.TransformColumns(ParsedDates, {{"DiscountRate", each if Text.EndsWith(Text.From(_), "%") then Number.FromText(Text.BeforeDelimiter(Text.From(_), "%")) / 100 else Number.FromText(Text.From(_)), type number}}),
    Typed = Table.TransformColumnTypes(ParsedDiscount, {{"Units", Int64.Type}, {"GrossSales", Currency.Type}, {"DiscountAmount", Currency.Type}, {"NetSales", Currency.Type}, {"CostOfGoodsSold", Currency.Type}, {"GrossProfit", Currency.Type}, {"ListUnitPrice", Currency.Type}}),
    RecoveredCost = Table.AddColumn(Typed, "ResolvedUnitCost", each if [UnitCost] = null or Text.Trim(Text.From([UnitCost])) = "" then Number.Round([CostOfGoodsSold] / [Units], 2) else Number.FromText(Text.From([UnitCost])), Currency.Type),
    RemovedOldCost = Table.RemoveColumns(RecoveredCost, {"UnitCost"}),
    RenamedCost = Table.RenameColumns(RemovedOldCost, {{"ResolvedUnitCost", "UnitCost"}}),
    FilledPromotion = Table.ReplaceValue(RenamedCost, each [PromotionName], each if ([PromotionName] = null or [PromotionName] = "") and [DiscountRate] = 0 then "No promotion" else [PromotionName], Replacer.ReplaceValue, {"PromotionName"}),
    ApprovedStores = Table.SelectRows(FilledPromotion, each List.Contains(DimStores[StoreID], [StoreID])),
    ApprovedProducts = Table.SelectRows(ApprovedStores, each List.Contains(DimProducts[ProductID], [ProductID]))
in
    ApprovedProducts

// Query: FactInventoryWeekly
let
    Source = fxLoadCsv("FactInventoryWeekly.csv"),
    Deduplicated = Table.Distinct(Source, {"InventoryRecordID"}),
    TrimmedKeys = Table.TransformColumns(Deduplicated, {{"StoreID", Text.Trim, type text}}),
    Typed = Table.TransformColumnTypes(TrimmedKeys, {{"WeekStartDate", type date}, {"ExpectedDemandUnits", Int64.Type}, {"FulfilledDemandUnits", Int64.Type}, {"EstimatedLostSales", Currency.Type}, {"EstimatedLostGrossProfit", Currency.Type}, {"AvailabilityRate", type number}})
in
    Typed

// Query: QuarantinedSales
// Keep rejected rows visible to the analyst instead of silently dropping them.
let
    Source = fxLoadCsv("FactSalesWeekly.csv"),
    Deduplicated = Table.Distinct(Source, {"SalesRecordID"}),
    Trimmed = Table.TransformColumns(Deduplicated, {{"StoreID", Text.Trim, type text}, {"ProductID", Text.Trim, type text}}),
    InvalidRows = Table.SelectRows(Trimmed, each not List.Contains(DimStores[StoreID], [StoreID]) or not List.Contains(DimProducts[ProductID], [ProductID]))
in
    InvalidRows

