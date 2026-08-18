"""Extra original curriculum tasks tagged to auto-approved sources.

Not copies of KA/OCW/MDN/SO pages. Distinct problems from the v0.4 bank.
"""

from __future__ import annotations

EXTRA_TASKS: dict[str, list[dict]] = {
    "khan_academy_computing": [
        {
            "task_type": "debugging_exercise",
            "concept_id": "python.conditionals",
            "language": "python",
            "prompt": "A learner writes `if score = 100:` expecting a perfect-score branch. What is wrong, and what should they write?",
            "answer": "A single equals is assignment and is a SyntaxError in that position. Use `if score == 100:`.",
            "solution": "Comparison uses ==. Assignment is a statement, not a boolean test there.",
        },
        {
            "task_type": "applied_exercise",
            "concept_id": "python.collections",
            "language": "python",
            "prompt": "You need unique words from a sentence while keeping first-seen order. Why is a set alone not enough in older Python mental models, and what does a dict do here?",
            "answer": "A set is unordered (historically). dict keys keep insertion order in modern CPython and are unique.",
            "solution": "dict.fromkeys(words) then list the keys. Do not sort unless the prompt asks for sorted unique words.",
        },
    ],
    "mit_opencourseware": [
        {
            "task_type": "simple_exercise",
            "concept_id": "cs.complexity",
            "language": "python",
            "prompt": "A loop runs n times; each iteration does a binary search on a sorted array of n items. What is Theta of the comparisons?",
            "answer": "Theta(n log n)",
            "solution": "n iterations times Theta(log n) per binary search.",
        },
        {
            "task_type": "applied_exercise",
            "concept_id": "cs.graphs",
            "language": "python",
            "prompt": "You have an unweighted maze on a grid. Why is BFS a better first choice than Dijkstra?",
            "answer": "Every edge has the same cost, so hop-count BFS already finds a shortest path. Dijkstra adds priority-queue overhead without changing the answer.",
            "solution": "Dijkstra generalizes BFS to nonnegative weights. Uniform weights make the extra machinery unnecessary.",
        },
    ],
    "harvard_cs50": [
        {
            "task_type": "debugging_exercise",
            "concept_id": "cs.os",
            "language": "c",
            "prompt": "A C program mallocs a buffer, copies a string without room for the NUL, then prints it. Name the defect class and the missing byte.",
            "answer": "Buffer overflow / missing terminator. strlen+1 bytes are required for a C string.",
            "solution": "C strings are NUL-terminated. strncpy without an explicit terminator is a common miss.",
        },
        {
            "task_type": "applied_exercise",
            "concept_id": "python.file_io",
            "language": "c",
            "prompt": "Why must you check fopen's return before fread, even if the path 'looks right'?",
            "answer": "fopen returns NULL on failure (missing file, permissions). Using the pointer is undefined.",
            "solution": "I/O can fail. Always branch on NULL and inspect errno or perror.",
        },
    ],
    "openstax": [
        {
            "task_type": "applied_exercise",
            "concept_id": "math.functions",
            "prompt": "A linear cost is C(n)=4n+12. What is the cost of 7 extra items relative to 0 items?",
            "answer": "28",
            "solution": "C(7)-C(0)=40-12=28. The intercept cancels; only the slope times 7 remains.",
            "numeric": {"got": 28, "expected": 28},
        },
        {
            "task_type": "simple_exercise",
            "concept_id": "math.sequences",
            "prompt": "The first three triangular numbers are 1, 3, 6. What is the 5th?",
            "answer": "15",
            "solution": "T_n = n(n+1)/2. T_5=15.",
            "numeric": {"got": 15, "expected": 15},
        },
    ],
    "mdn": [
        {
            "task_type": "applied_exercise",
            "concept_id": "javascript.promises",
            "language": "javascript",
            "prompt": "Why does `fetch(url).then(r => r.json()).then(data => data)` still need error handling for HTTP 404?",
            "answer": "fetch only rejects on network failure. HTTP 404 is a fulfilled Promise with ok=false. Check r.ok or r.status.",
            "solution": "Treat non-2xx as an application error. catch() does not see them unless you throw.",
        },
        {
            "task_type": "debugging_exercise",
            "concept_id": "javascript.closures",
            "language": "javascript",
            "prompt": "An event handler is added inside a loop with `var i` and later logs i. Why is it the last i, and what binding fixes it?",
            "answer": "var is function-scoped, so every handler shares one i. Use let, or pass i into a factory.",
            "solution": "let creates a per-iteration binding. Closures capture bindings, not snapshots of numbers.",
        },
    ],
    "the_odin_project": [
        {
            "task_type": "applied_exercise",
            "concept_id": "cs.git",
            "language": "javascript",
            "prompt": "You committed a secret to main and pushed. Why is deleting the file in a new commit not enough, and what must you still do?",
            "answer": "The secret remains in git history and clones. Rotate the credential; history rewrite only helps unpushed or coordinated force-push, which still leaks if others fetched.",
            "solution": "Treat leaked secrets as compromised. git rm does not unsay old blobs.",
        },
        {
            "task_type": "concept_explanation",
            "concept_id": "cs.http",
            "language": "javascript",
            "prompt": "Why is storing a session identifier in a non-HttpOnly cookie riskier than an HttpOnly cookie?",
            "answer": "JavaScript on the page can read a non-HttpOnly cookie, so XSS can steal the session. HttpOnly hides it from document.cookie.",
            "solution": "HttpOnly is not a complete XSS defense, but it removes one theft path. Still validate and encode output.",
        },
    ],
    "python_docs": [
        {
            "task_type": "simple_exercise",
            "concept_id": "python.comprehensions",
            "language": "python",
            "prompt": "What does `{k: v for k, v in [('a', 1), ('a', 2)]}` evaluate to, and why is there one key?",
            "answer": "{'a': 2}",
            "solution": "Dict displays last-write-wins for duplicate keys. The second pair overwrites.",
        },
        {
            "task_type": "applied_exercise",
            "concept_id": "python.context_managers",
            "language": "python",
            "prompt": "Why is `f = open(path); data = f.read(); f.close()` weaker than a with-block when read() can raise?",
            "answer": "If read raises, close is skipped. with always runs __exit__.",
            "solution": "try/finally is the manual equivalent. with is the standard spelling.",
        },
        {
            "task_type": "concept_explanation",
            "concept_id": "python.typing",
            "language": "python",
            "prompt": "What is the difference between `list` and `list[int]` in a function annotation?",
            "answer": "`list` says it is a list. `list[int]` additionally says checkers should expect integer elements.",
            "solution": "CPython does not enforce the parameter. Type checkers do.",
        },
    ],
    "rust_docs": [
        {
            "task_type": "applied_exercise",
            "language": "rust",
            "prompt": "When would you clone a String to satisfy the borrow checker, and when is that a design smell?",
            "answer": "Clone when you truly need two owned values. It is a smell if a borrow or restructuring would have been enough.",
            "solution": "Clones allocate. Prefer &str, lifetimes, or moving once.",
        },
        {
            "task_type": "debugging_exercise",
            "language": "rust",
            "prompt": "You hold an immutable borrow of a Vec and try to push. Why does that fail, and what API change would make the intent legal?",
            "answer": "push needs &mut self. An outstanding &T borrow forbids &mut T. End the immutable borrow first, or don't hold it across the mutation.",
            "solution": "NLL still cannot allow aliased mutation. Split the scopes.",
        },
    ],
    "go_docs": [
        {
            "task_type": "applied_exercise",
            "language": "go",
            "prompt": "Why should you not close a channel from the receiver side in a typical worker pool?",
            "answer": "Close is a signal from senders that no more values will be sent. Receivers closing can panic senders still sending.",
            "solution": "Sender closes; receivers range until close. Coordinate shutdown with WaitGroup and a done channel if needed.",
        },
        {
            "task_type": "debugging_exercise",
            "language": "go",
            "prompt": "A function locks a mutex, then calls a callback that tries to lock the same mutex. What happens with a non-reentrant mutex, and how do you avoid it?",
            "answer": "Deadlock: the same goroutine waits for a lock it already holds. Do not call user callbacks while holding the lock, or use a documented reentrant design (not standard mutex).",
            "solution": "Keep critical sections small. Copy data, unlock, then callback.",
        },
    ],
    "w3c_whatwg": [
        {
            "task_type": "applied_exercise",
            "language": "html",
            "prompt": "Why is `div` with a click handler a poor substitute for a `button` that submits a form?",
            "answer": "A div is not a form-associated submit control, is not keyboard-activated by default, and lacks button semantics for assistive tech.",
            "solution": "Use button type=submit. If you must use another element, you must reconstruct keyboard, role, and form behavior.",
        },
        {
            "task_type": "concept_explanation",
            "language": "html",
            "prompt": "What does a unique `id` on a page enable for a label's `for` attribute?",
            "answer": "The label can point at that control, so clicking the label focuses/activates it and assistive tech can name it.",
            "solution": "Duplicate ids break the association. One id per document.",
        },
    ],
    "sqlite_docs": [
        {
            "task_type": "applied_exercise",
            "language": "sql",
            "prompt": "Why can `SELECT * FROM t WHERE x = 1 OR y = 2` be hard to index well with a single B-tree on (x)?",
            "answer": "The OR means rows matching only y still qualify, so an index on x cannot find them. Often you need a second index or a UNION of two index lookups.",
            "solution": "OR across different columns fights a single-column index. AND of indexed prefixes is easier.",
        },
        {
            "task_type": "simple_exercise",
            "concept_id": "cs.sql",
            "language": "sql",
            "prompt": "In SQLite, what does COUNT(*) return on a table with 3 rows including one all-NULL row?",
            "answer": "3",
            "solution": "COUNT(*) counts rows, not non-NULL values. COUNT(column) would skip NULLs in that column.",
            "numeric": {"got": 3, "expected": 3},
        },
    ],
    "postgresql_docs": [
        {
            "task_type": "applied_exercise",
            "language": "sql",
            "prompt": "Why might a sequential scan beat an index on a query that matches 90% of a table?",
            "answer": "Random I/O into most of the heap can be slower than one sequential read. Selectivity is too low for the index to win.",
            "solution": "Indexes help selective predicates. The planner compares costs; high match rate favors seq scan.",
        },
        {
            "task_type": "concept_explanation",
            "concept_id": "sql.indexes",
            "language": "sql",
            "prompt": "What is a covering index in PostgreSQL terms (Index Only Scan), and what extra data makes it possible?",
            "answer": "The index contains all columns the query needs, so PostgreSQL can avoid heap fetches when visibility allows.",
            "solution": "INCLUDE columns or a matching btree of selected columns. VACUUM/visibility maps still matter.",
        },
    ],
    "linux_man_pages": [
        {
            "task_type": "applied_exercise",
            "language": "c",
            "prompt": "Why can `malloc` returning NULL be more likely after a huge allocation than a 16-byte one, and what must the caller do?",
            "answer": "The allocator may not find a large enough contiguous region (or hit limits). Check for NULL before writing.",
            "solution": "OOM is a normal failure. Dereferencing NULL is not.",
        },
        {
            "task_type": "debugging_exercise",
            "language": "c",
            "prompt": "A program uses `gets` to read a line. Why is that always a defect even if the input 'is usually short'?",
            "answer": "gets cannot bound the write. Any longer line overruns the buffer. Use fgets or similar with a size.",
            "solution": "Unbounded C string APIs are unsafe. Size belongs in the API.",
        },
    ],
    "nasa_education": [
        {
            "task_type": "simple_exercise",
            "concept_id": "science.energy",
            "prompt": "A 4 kg probe moves at 5 m/s. What is its kinetic energy in joules?",
            "answer": "50",
            "solution": "KE=1/2 m v^2 = 0.5*4*25=50.",
            "numeric": {"got": 50, "expected": 50},
        },
        {
            "task_type": "concept_explanation",
            "concept_id": "science.newton",
            "prompt": "In deep space with negligible gravity, why does a spacecraft keep moving after the engine cuts off?",
            "answer": "No net force means constant velocity. Thrust was needed to change speed, not to keep moving.",
            "solution": "Newton's first law. Drag is what makes Earth intuition different.",
        },
    ],
    "noaa_education": [
        {
            "task_type": "applied_exercise",
            "concept_id": "science.method",
            "prompt": "A coastal sensor fails for three days during a storm. Why must a monthly mean sea-level plot disclose that gap?",
            "answer": "The mean would silently omit the storm surge days. Missingness is information, not a reason to pretend the series is complete.",
            "solution": "Document coverage. Imputation is a separate, declared step.",
        },
        {
            "task_type": "simple_exercise",
            "concept_id": "science.waves",
            "prompt": "A water wave has period 4 s and wavelength 8 m. What is the speed in m/s?",
            "answer": "2",
            "solution": "v=λ/T=8/4=2.",
            "numeric": {"got": 2, "expected": 2},
        },
    ],
    "usgs_education": [
        {
            "task_type": "applied_exercise",
            "concept_id": "science.method",
            "prompt": "Two seismometers record the same quake with different peak accelerations. Give two non-instrument-failure reasons.",
            "answer": "Different distance/azimuth from the rupture, and different site geology (amplification on sediments vs rock).",
            "solution": "Intensity is local. Magnitude is a source estimate.",
        },
        {
            "task_type": "simple_exercise",
            "concept_id": "science.energy",
            "prompt": "A 2 kg rock falls 5 m. Taking g=10 m/s^2 and PE=mgh, what is the loss of gravitational PE in joules?",
            "answer": "100",
            "solution": "mgh=2*10*5=100 J.",
            "numeric": {"got": 100, "expected": 100},
        },
    ],
    "oer_commons": [
        {
            "task_type": "applied_exercise",
            "prompt": "A worksheet is labeled 'free to use in class' with no SPDX. Can Open Reason copy it into a CC BY 4.0 dataset?",
            "answer": "No. Informal permission is not a clear redistribution license. Leave it out or obtain an explicit license.",
            "solution": "Public posting is not CC BY. Ambiguous licenses stay out of the release.",
        },
        {
            "task_type": "concept_explanation",
            "prompt": "Why is attribution still required for CC BY even when commercial use is allowed?",
            "answer": "BY means you must credit the licensor in the manner they request, commercially or not.",
            "solution": "Commercial rights and attribution are separate license axes.",
        },
    ],
    "wikibooks": [
        {
            "task_type": "applied_exercise",
            "prompt": "You rewrite a CC BY-SA paragraph in your own words but keep the same examples and structure. Why might share-alike still attach?",
            "answer": "A close adaptation can still be a derivative. SA follows derivatives. If unsure, do not include it in a non-SA corpus.",
            "solution": "Paraphrase is not a clean room. Original tasks with independent examples avoid the issue.",
        },
        {
            "task_type": "concept_explanation",
            "prompt": "What does 'compatible share-alike' mean when combining two SA works?",
            "answer": "The combination must be released under a license the originals permit for derivatives, usually the same SA family.",
            "solution": "You cannot wash SA off by mixing with CC BY-only text in one redistributed unit.",
        },
    ],
}
