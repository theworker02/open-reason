"""SQL (SQLite) and JavaScript tasks with executable verification."""

from __future__ import annotations

from typing import Any

SqlTask = dict[str, Any]
JsTask = dict[str, Any]


SQL_TASKS: list[SqlTask] = [
    {
        "slug": "dept_headcount",
        "topic": "sql",
        "prompt": (
            "Tables: employees(id, dept, salary). Write a SQL query that returns "
            "dept and headcount for departments with at least 2 employees, "
            "ordered by headcount descending, then dept ascending."
        ),
        "schema": """
CREATE TABLE employees (id INTEGER, dept TEXT, salary INTEGER);
INSERT INTO employees VALUES
  (1, 'eng', 100), (2, 'eng', 110), (3, 'eng', 90),
  (4, 'hr', 70), (5, 'sales', 80), (6, 'sales', 85);
""",
        "query": """
SELECT dept, COUNT(*) AS headcount
FROM employees
GROUP BY dept
HAVING COUNT(*) >= 2
ORDER BY headcount DESC, dept ASC;
""",
        "expected": [("eng", 3), ("sales", 2)],
    },
    {
        "slug": "inner_join_orders",
        "topic": "sql",
        "prompt": (
            "customers(id, name), orders(id, customer_id, total). Return customer name "
            "and order total for orders with total >= 50, ordered by total descending."
        ),
        "schema": """
CREATE TABLE customers (id INTEGER, name TEXT);
CREATE TABLE orders (id INTEGER, customer_id INTEGER, total INTEGER);
INSERT INTO customers VALUES (1, 'Ada'), (2, 'Ben'), (3, 'Cyd');
INSERT INTO orders VALUES (10, 1, 40), (11, 1, 80), (12, 2, 50), (13, 3, 10);
""",
        "query": """
SELECT c.name, o.total
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.id
WHERE o.total >= 50
ORDER BY o.total DESC, c.name ASC;
""",
        "expected": [("Ada", 80), ("Ben", 50)],
    },
    {
        "slug": "left_join_missing",
        "topic": "sql",
        "prompt": (
            "users(id, name), logins(user_id). Return each user name and their login "
            "count, including users with zero logins, ordered by name."
        ),
        "schema": """
CREATE TABLE users (id INTEGER, name TEXT);
CREATE TABLE logins (user_id INTEGER);
INSERT INTO users VALUES (1, 'a'), (2, 'b'), (3, 'c');
INSERT INTO logins VALUES (1), (1), (3);
""",
        "query": """
SELECT u.name, COUNT(l.user_id) AS n
FROM users AS u
LEFT JOIN logins AS l ON l.user_id = u.id
GROUP BY u.id, u.name
ORDER BY u.name;
""",
        "expected": [("a", 2), ("b", 0), ("c", 1)],
    },
    {
        "slug": "running_sum_window",
        "topic": "sql",
        "prompt": (
            "events(day, amount) with one row per day. Return day and a running sum "
            "of amount ordered by day (SQLite window functions)."
        ),
        "schema": """
CREATE TABLE events (day INTEGER, amount INTEGER);
INSERT INTO events VALUES (1, 5), (2, 3), (3, 8);
""",
        "query": """
SELECT day, SUM(amount) OVER (ORDER BY day ROWS UNBOUNDED PRECEDING) AS running
FROM events
ORDER BY day;
""",
        "expected": [(1, 5), (2, 8), (3, 16)],
    },
    {
        "slug": "top_per_group",
        "topic": "sql",
        "prompt": (
            "scores(student, course, score). Return the student with the highest score "
            "in each course (break ties by student name ascending). Columns: course, student, score."
        ),
        "schema": """
CREATE TABLE scores (student TEXT, course TEXT, score INTEGER);
INSERT INTO scores VALUES
  ('ann', 'math', 90), ('bob', 'math', 90), ('ann', 'cs', 70), ('bob', 'cs', 95);
""",
        "query": """
WITH ranked AS (
  SELECT course, student, score,
         ROW_NUMBER() OVER (PARTITION BY course ORDER BY score DESC, student ASC) AS rk
  FROM scores
)
SELECT course, student, score FROM ranked WHERE rk = 1 ORDER BY course;
""",
        "expected": [("cs", "bob", 95), ("math", "ann", 90)],
    },
    {
        "slug": "anti_join_unmatched",
        "topic": "sql",
        "prompt": (
            "parts(id), used(part_id). Return ids of parts that were never used, ordered."
        ),
        "schema": """
CREATE TABLE parts (id INTEGER);
CREATE TABLE used (part_id INTEGER);
INSERT INTO parts VALUES (1), (2), (3), (4);
INSERT INTO used VALUES (2), (2), (4);
""",
        "query": """
SELECT p.id
FROM parts AS p
WHERE NOT EXISTS (SELECT 1 FROM used u WHERE u.part_id = p.id)
ORDER BY p.id;
""",
        "expected": [(1,), (3,)],
    },
    {
        "slug": "case_buckets",
        "topic": "sql",
        "prompt": (
            "temps(celsius). Bucket into 'cold' (<10), 'mild' [10,25], 'hot' (>25) "
            "and return bucket, n ordered by n descending, bucket ascending."
        ),
        "schema": """
CREATE TABLE temps (celsius INTEGER);
INSERT INTO temps VALUES (0), (5), (10), (20), (25), (30), (40);
""",
        "query": """
SELECT CASE
         WHEN celsius < 10 THEN 'cold'
         WHEN celsius <= 25 THEN 'mild'
         ELSE 'hot'
       END AS bucket,
       COUNT(*) AS n
FROM temps
GROUP BY bucket
ORDER BY n DESC, bucket ASC;
""",
        "expected": [("mild", 3), ("cold", 2), ("hot", 2)],
    },
    {
        "slug": "self_join_org",
        "topic": "sql",
        "prompt": (
            "staff(id, name, manager_id). Return employee name and manager name for "
            "employees who have a manager, ordered by employee name."
        ),
        "schema": """
CREATE TABLE staff (id INTEGER, name TEXT, manager_id INTEGER);
INSERT INTO staff VALUES (1, 'root', NULL), (2, 'lee', 1), (3, 'sam', 1), (4, 'pat', 2);
""",
        "query": """
SELECT e.name AS employee, m.name AS manager
FROM staff AS e
JOIN staff AS m ON e.manager_id = m.id
ORDER BY e.name;
""",
        "expected": [("lee", "root"), ("pat", "lee"), ("sam", "root")],
    },
    {
        "slug": "distinct_active",
        "topic": "sql",
        "prompt": (
            "sessions(user_id, active INTEGER 0/1). How many distinct users have at "
            "least one active session? Return a single column n."
        ),
        "schema": """
CREATE TABLE sessions (user_id INTEGER, active INTEGER);
INSERT INTO sessions VALUES (1, 0), (1, 1), (2, 0), (3, 1), (3, 1);
""",
        "query": """
SELECT COUNT(DISTINCT user_id) AS n
FROM sessions
WHERE active = 1;
""",
        "expected": [(2,)],
    },
    {
        "slug": "date_diff_sqlite",
        "topic": "sql",
        "prompt": (
            "events(name, ts TEXT as YYYY-MM-DD). Return name and days since 2026-01-01 "
            "for each event (julianday difference as integer), ordered by name."
        ),
        "schema": """
CREATE TABLE events (name TEXT, ts TEXT);
INSERT INTO events VALUES ('a', '2026-01-11'), ('b', '2026-01-01');
""",
        "query": """
SELECT name, CAST(julianday(ts) - julianday('2026-01-01') AS INTEGER) AS days
FROM events
ORDER BY name;
""",
        "expected": [("a", 10), ("b", 0)],
    },
    {
        "slug": "update_style_select",
        "topic": "sql",
        "prompt": (
            "prices(sku, cents). Return sku and a discounted price: 10% off using "
            "integer arithmetic (cents * 9 / 10), ordered by sku."
        ),
        "schema": """
CREATE TABLE prices (sku TEXT, cents INTEGER);
INSERT INTO prices VALUES ('aa', 1000), ('bb', 50);
""",
        "query": """
SELECT sku, (cents * 9) / 10 AS discounted
FROM prices
ORDER BY sku;
""",
        "expected": [("aa", 900), ("bb", 45)],
    },
    {
        "slug": "having_avg",
        "topic": "sql",
        "prompt": (
            "reviews(product, stars). Return products whose average stars are at least "
            "4.0, with avg_stars rounded to 2 decimals via ROUND, ordered by product."
        ),
        "schema": """
CREATE TABLE reviews (product TEXT, stars INTEGER);
INSERT INTO reviews VALUES ('p', 5), ('p', 4), ('q', 3), ('q', 3), ('r', 5);
""",
        "query": """
SELECT product, ROUND(AVG(stars), 2) AS avg_stars
FROM reviews
GROUP BY product
HAVING AVG(stars) >= 4.0
ORDER BY product;
""",
        "expected": [("p", 4.5), ("r", 5.0)],
    },
    {
        "slug": "select_distinct",
        "topic": "sql",
        "prompt": (
            "tags(item, tag). Return distinct tags in alphabetical order."
        ),
        "schema": """
CREATE TABLE tags (item TEXT, tag TEXT);
INSERT INTO tags VALUES ('a', 'x'), ('b', 'y'), ('c', 'x'), ('d', 'z');
""",
        "query": """
SELECT DISTINCT tag
FROM tags
ORDER BY tag;
""",
        "expected": [("x",), ("y",), ("z",)],
    },
    {
        "slug": "case_bucket",
        "topic": "sql",
        "prompt": (
            "scores(id, n). Return id and band where n>=80 is 'high', n>=50 is 'mid', else 'low', "
            "ordered by id."
        ),
        "schema": """
CREATE TABLE scores (id INTEGER, n INTEGER);
INSERT INTO scores VALUES (1, 90), (2, 50), (3, 20);
""",
        "query": """
SELECT id,
  CASE
    WHEN n >= 80 THEN 'high'
    WHEN n >= 50 THEN 'mid'
    ELSE 'low'
  END AS band
FROM scores
ORDER BY id;
""",
        "expected": [(1, "high"), (2, "mid"), (3, "low")],
    },
    {
        "slug": "self_join_mgr",
        "topic": "sql",
        "prompt": (
            "staff(id, name, manager_id). Return employee name and manager name for "
            "employees who have a manager, ordered by employee name."
        ),
        "schema": """
CREATE TABLE staff (id INTEGER, name TEXT, manager_id INTEGER);
INSERT INTO staff VALUES (1, 'Ada', NULL), (2, 'Ben', 1), (3, 'Cyd', 1);
""",
        "query": """
SELECT e.name AS employee, m.name AS manager
FROM staff AS e
JOIN staff AS m ON e.manager_id = m.id
ORDER BY e.name;
""",
        "expected": [("Ben", "Ada"), ("Cyd", "Ada")],
    },
]


JS_TASKS: list[JsTask] = [
    {
        "slug": "stable_sort_key",
        "topic": "javascript",
        "prompt": (
            "Implement function sortBy(items, key) that returns a new array sorted by "
            "the numeric key, stable with respect to original order."
        ),
        "code": """
function sortBy(items, key) {
  return items
    .map((item, index) => ({ item, index }))
    .sort((a, b) => {
      const d = key(a.item) - key(b.item);
      return d !== 0 ? d : a.index - b.index;
    })
    .map((row) => row.item);
}
module.exports = { sortBy };
""",
        "tests": """
const assert = require('assert');
const { sortBy } = require('./solution');
const got = sortBy(
  [{ n: 2, id: 'a' }, { n: 1, id: 'b' }, { n: 2, id: 'c' }],
  (x) => x.n
);
assert.deepStrictEqual(got.map((x) => x.id), ['b', 'a', 'c']);
console.log('OPEN_REASON_RESULT ' + JSON.stringify({ passed: true, tests_run: 1, failures: 0, errors: 0 }));
""",
    },
    {
        "slug": "deep_freeze_guard",
        "topic": "javascript",
        "prompt": (
            "Implement deepFreeze(obj) that recursively Object.freeze arrays and plain "
            "objects and returns the same reference. Ignore functions."
        ),
        "code": """
function deepFreeze(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  Object.freeze(obj);
  for (const value of Object.values(obj)) {
    deepFreeze(value);
  }
  return obj;
}
module.exports = { deepFreeze };
""",
        "tests": """
const assert = require('assert');
const { deepFreeze } = require('./solution');
const o = { a: { b: 1 } };
deepFreeze(o);
assert.ok(Object.isFrozen(o) && Object.isFrozen(o.a));
console.log('OPEN_REASON_RESULT ' + JSON.stringify({ passed: true, tests_run: 1, failures: 0, errors: 0 }));
""",
    },
    {
        "slug": "promise_pool",
        "topic": "javascript",
        "prompt": (
            "Implement async function pool(limit, factories) where factories is an array "
            "of () => Promise. Run at most `limit` at once. Return results in factory order."
        ),
        "code": """
async function pool(limit, factories) {
  const results = new Array(factories.length);
  let next = 0;
  async function worker() {
    while (true) {
      const i = next++;
      if (i >= factories.length) return;
      results[i] = await factories[i]();
    }
  }
  const n = Math.min(limit, factories.length);
  await Promise.all(Array.from({ length: n }, () => worker()));
  return results;
}
module.exports = { pool };
""",
        "tests": """
const assert = require('assert');
const { pool } = require('./solution');
(async () => {
  let current = 0;
  let max = 0;
  const factories = [0, 1, 2, 3, 4].map((i) => async () => {
    current += 1;
    max = Math.max(max, current);
    await new Promise((r) => setTimeout(r, 20));
    current -= 1;
    return i * 2;
  });
  const got = await pool(2, factories);
  assert.deepStrictEqual(got, [0, 2, 4, 6, 8]);
  assert.ok(max <= 2);
  console.log('OPEN_REASON_RESULT ' + JSON.stringify({ passed: true, tests_run: 2, failures: 0, errors: 0 }));
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
""",
    },
    {
        "slug": "url_query_merge",
        "topic": "javascript",
        "prompt": (
            "Implement mergeQuery(url, params) using the WHATWG URL class. Overlay "
            "params (object of string values) onto the existing search params and "
            "return href without changing other components."
        ),
        "code": """
function mergeQuery(url, params) {
  const u = new URL(url);
  for (const [k, v] of Object.entries(params)) {
    u.searchParams.set(k, v);
  }
  return u.href;
}
module.exports = { mergeQuery };
""",
        "tests": """
const assert = require('assert');
const { mergeQuery } = require('./solution');
const got = mergeQuery('https://example.com/path?q=1&x=2', { x: '9', y: 'z' });
assert.strictEqual(got, 'https://example.com/path?q=1&x=9&y=z');
console.log('OPEN_REASON_RESULT ' + JSON.stringify({ passed: true, tests_run: 1, failures: 0, errors: 0 }));
""",
    },
    {
        "slug": "ts_like_omit",
        "topic": "javascript",
        "prompt": (
            "Implement omit(obj, keys) returning a shallow clone without the listed keys."
        ),
        "code": """
function omit(obj, keys) {
  const skip = new Set(keys);
  const out = {};
  for (const [k, v] of Object.entries(obj)) {
    if (!skip.has(k)) out[k] = v;
  }
  return out;
}
module.exports = { omit };
""",
        "tests": """
const assert = require('assert');
const { omit } = require('./solution');
assert.deepStrictEqual(omit({ a: 1, b: 2, c: 3 }, ['b']), { a: 1, c: 3 });
console.log('OPEN_REASON_RESULT ' + JSON.stringify({ passed: true, tests_run: 1, failures: 0, errors: 0 }));
""",
    },
    {
        "slug": "binary_search_js",
        "topic": "javascript",
        "prompt": (
            "Implement lowerBound(arr, target) on a sorted numeric array: first index "
            "with arr[i] >= target, or arr.length."
        ),
        "code": """
function lowerBound(arr, target) {
  let lo = 0;
  let hi = arr.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid] < target) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}
module.exports = { lowerBound };
""",
        "tests": """
const assert = require('assert');
const { lowerBound } = require('./solution');
assert.strictEqual(lowerBound([1, 3, 3, 7], 3), 1);
assert.strictEqual(lowerBound([1, 3, 7], 8), 3);
console.log('OPEN_REASON_RESULT ' + JSON.stringify({ passed: true, tests_run: 2, failures: 0, errors: 0 }));
""",
    },
    {
        "slug": "event_debounce",
        "topic": "javascript",
        "prompt": (
            "Implement debounce(fn, wait) using setTimeout. Leading calls reset the timer. "
            "Return a function that forwards this and arguments."
        ),
        "code": """
function debounce(fn, wait) {
  let timer = null;
  return function (...args) {
    const ctx = this;
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(ctx, args), wait);
  };
}
module.exports = { debounce };
""",
        "tests": """
const assert = require('assert');
const { debounce } = require('./solution');
(async () => {
  let n = 0;
  const f = debounce(() => { n += 1; }, 30);
  f(); f(); f();
  await new Promise((r) => setTimeout(r, 80));
  assert.strictEqual(n, 1);
  console.log('OPEN_REASON_RESULT ' + JSON.stringify({ passed: true, tests_run: 1, failures: 0, errors: 0 }));
})().catch((err) => { console.error(err); process.exit(1); });
""",
    },
    {
        "slug": "csv_line",
        "topic": "javascript",
        "prompt": (
            "Implement parseCsvLine(line) splitting on commas, supporting double-quoted "
            "fields with doubled quotes as escape. Return string[]."
        ),
        "code": """
function parseCsvLine(line) {
  const out = [];
  let cur = '';
  let i = 0;
  let inQuotes = false;
  while (i < line.length) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (line[i + 1] === '"') { cur += '"'; i += 2; continue; }
        inQuotes = false; i += 1; continue;
      }
      cur += ch; i += 1; continue;
    }
    if (ch === '"') { inQuotes = true; i += 1; continue; }
    if (ch === ',') { out.push(cur); cur = ''; i += 1; continue; }
    cur += ch; i += 1;
  }
  out.push(cur);
  return out;
}
module.exports = { parseCsvLine };
""",
        "tests": """
const assert = require('assert');
const { parseCsvLine } = require('./solution');
assert.deepStrictEqual(parseCsvLine('a,"b,c","d""e"'), ['a', 'b,c', 'd"e']);
console.log('OPEN_REASON_RESULT ' + JSON.stringify({ passed: true, tests_run: 1, failures: 0, errors: 0 }));
""",
    },
]
