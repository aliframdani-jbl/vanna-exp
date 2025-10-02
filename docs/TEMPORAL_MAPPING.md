# Temporal Expression Mapping for Text2SQL

## 📅 **Precise Time Period Definitions**

Your analysis is spot-on! Here's the standardized mapping for temporal expressions:

### **🇮🇩 Indonesian → 🇬🇧 English → 💻 SQL Pattern**

| Indonesian | English | Meaning | ClickHouse SQL Pattern |
|------------|---------|---------|------------------------|
| **Rolling Time Periods** |
| `7 hari terakhir` | "past 7 days" | Last 7×24 hours from now | `WHERE created_date >= today() - 7` |
| `30 hari terakhir` | "past 30 days" | Last 30×24 hours from now | `WHERE created_date >= today() - 30` |
| **Calendar Weeks** |
| `minggu ini` | "this week" | Current Mon-Sun week | `WHERE created_date >= toStartOfWeek(today())` |
| `minggu lalu` | "last week" | Previous Mon-Sun week | `WHERE created_date >= toStartOfWeek(today()) - 7 AND created_date < toStartOfWeek(today())` |
| **Calendar Months** |
| `bulan ini` | "this month" | Current calendar month | `WHERE toMonth(created_date) = toMonth(today()) AND toYear(created_date) = toYear(today())` |
| `bulan lalu` | "last month" | Previous calendar month | `WHERE toMonth(created_date) = toMonth(today()) - 1 AND toYear(created_date) = toYear(today())` |
| **Calendar Years** |
| `tahun ini` | "this year" | Current calendar year | `WHERE toYear(created_date) = toYear(now())` |
| `tahun lalu` | "last year" | Previous calendar year | `WHERE toYear(created_date) = toYear(now()) - 1` |

---

## ⚠️ **Common Mistakes to Avoid**

### ❌ **Wrong Interpretations:**

1. **"minggu lalu" → `WHERE created_date >= today() - 7`**
   - This is "7 hari terakhir", not "minggu lalu"
   - Covers 7×24 hours, not calendar week

2. **"minggu lalu" → `WHERE created_date >= toStartOfWeek(now()) - 7`**
   - This is 10+ days (depends on current day)
   - Not a clean week boundary

3. **Using INTERVAL syntax in ClickHouse**
   - `INTERVAL 7 DAY` doesn't exist in ClickHouse
   - Use arithmetic: `today() - 7`

---

## ✅ **Correct Examples**

### **Scenario: Today is Wednesday, Oct 2, 2024**

```sql
-- ✅ "7 hari terakhir" (Sep 25 10:00 → Oct 2 10:00)
SELECT COUNT(*) FROM internal.realtime_order 
WHERE created_date >= today() - 7

-- ✅ "minggu lalu" (Sep 23 00:00 → Sep 29 23:59)
SELECT COUNT(*) FROM internal.realtime_order 
WHERE created_date >= toStartOfWeek(today()) - 7 
  AND created_date < toStartOfWeek(today())

-- ✅ "minggu ini" (Sep 30 00:00 → now)
SELECT COUNT(*) FROM internal.realtime_order 
WHERE created_date >= toStartOfWeek(today())

-- ✅ "bulan ini" (Oct 1 → Oct 31)
SELECT COUNT(*) FROM internal.realtime_order 
WHERE toMonth(created_date) = toMonth(today()) 
  AND toYear(created_date) = toYear(today())

-- ✅ "tahun ini" (Jan 1 → Dec 31)
SELECT COUNT(*) FROM internal.realtime_order 
WHERE toYear(created_date) = toYear(now())
```

---

## 🎯 **Advanced Temporal Patterns**

### **Quarter Handling:**
```sql
-- Q1 this year (Jan-Mar)
WHERE toQuarter(created_date) = 1 AND toYear(created_date) = toYear(now())

-- Last quarter
WHERE toQuarter(created_date) = toQuarter(now()) - 1 
  AND toYear(created_date) = toYear(now())
```

### **Business Day Patterns:**
```sql
-- Weekdays only (Mon-Fri)
WHERE toDayOfWeek(created_date) BETWEEN 1 AND 5

-- Weekend only (Sat-Sun)  
WHERE toDayOfWeek(created_date) IN (6, 7)
```

### **Hour-specific Patterns:**
```sql
-- Business hours (9 AM - 5 PM)
WHERE toHour(created_date) BETWEEN 9 AND 17

-- Today so far
WHERE toDate(created_date) = today()
```

---

## 🧪 **Test Cases for Validation**

```bash
# Test rolling vs calendar periods
"pesanan 7 hari terakhir"     → today() - 7
"pesanan minggu lalu"         → calendar week boundaries
"pendapatan bulan ini"        → toMonth() = toMonth(today())
"total penjualan tahun ini"   → toYear() = toYear(now())
```

---

## 💡 **Implementation Tips**

1. **Always clarify ambiguous requests:**
   - "minggu lalu" → ask "calendar week or past 7 days?"
   - Default to calendar periods for business reports

2. **Use consistent terminology:**
   - "hari terakhir" = rolling days
   - "minggu/bulan/tahun lalu" = calendar periods

3. **Consider timezone handling:**
   - ClickHouse `today()` uses server timezone
   - May need `toDate(now(), 'Asia/Jakarta')` for Indonesian business

4. **Validate with business context:**
   - Monday reports usually want "last week" = previous Mon-Sun
   - End-of-month reports want full calendar months

This mapping ensures your Text2SQL generates precise, business-meaningful queries! 🎯