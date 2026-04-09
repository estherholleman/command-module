---
name: debug-notebook
description: Diagnose why a Jupyter notebook cell produces wrong output, empty output, or errors. Use when a notebook cell isn't behaving as expected — especially when the cause isn't obvious from the traceback.
argument-hint: "[optional: brief description of the symptom]"
---

# Debug Notebook

A triage-first diagnostic workflow for Jupyter notebook problems. Designed for data science notebooks running in VS Code, Cursor, or JupyterLab.

Notebook failures have a different taxonomy than application bugs. Before reading code or inspecting data, first identify *which layer* is broken. This prevents the most common debugging trap: spending 20 minutes checking data and code when the problem is a broken widget renderer or stale kernel.

## The Failure Layers

Notebook problems live in one of five layers. They are listed in diagnostic order — cheapest to test first.

| Layer | Symptoms | Test cost |
|-------|----------|-----------|
| **1. Rendering** | Cell runs (green check, timing shown) but output is blank or invisible. Widgets don't appear. Plots don't display. | 5 seconds |
| **2. Kernel / Environment** | Import errors. Missing attributes on packages. Functions that "should exist" don't. Version mismatches. | 10 seconds |
| **3. Cell State** | NameError for variables that are defined "above." Stale values from a previous run. Works after Restart & Run All but not when running individual cells. | 15 seconds |
| **4. Data Pipeline** | Cell runs without error but produces empty output because a DataFrame is empty, a filter matches nothing, or an upstream cell didn't populate a variable. | 15 seconds |
| **5. Code Logic** | Wrong output. Incorrect calculations. Plot shows unexpected values. Function returns None when it shouldn't. | varies |

## Phase 1: Identify the Symptom Class

Before doing anything else, classify what the user is seeing. Ask if not obvious:

- **Blank output** — cell executes (shows timing) but nothing visible appears
- **Error** — cell throws an exception with a traceback
- **Empty result** — output renders but contains no data (empty DataFrame, "0 results", blank plot axes)
- **Wrong result** — output appears but values are incorrect
- **Hang / no completion** — cell never finishes executing

This classification determines which layer to test first:

| Symptom | Most likely layer | Start with |
|---------|-------------------|------------|
| Blank output | Rendering | Phase 2A |
| Error | Kernel/Environment or Code | Read the traceback first |
| Empty result | Data Pipeline | Phase 2D |
| Wrong result | Code Logic | Phase 2E |
| Hang | Kernel or Code (infinite loop, deadlock) | Phase 2B |

## Phase 2: Layer Isolation Tests

Run the relevant isolation test. Each test should take under 30 seconds. Do NOT skip ahead to code inspection — the whole point is to rule out environmental problems first.

### 2A: Rendering Test (for blank output)

Run a minimal test in a new cell to check if the output system itself works:

**For widget problems:**
```python
import ipywidgets as widgets
from IPython.display import display
display(widgets.IntSlider(value=5, min=0, max=10, description="Test:"))
```

**For plot problems:**
```python
import matplotlib.pyplot as plt
plt.figure(figsize=(3, 2))
plt.plot([1, 2, 3], [1, 4, 9])
plt.title("Render test")
plt.show()
```

**For HTML/rich display problems:**
```python
from IPython.display import display, HTML
display(HTML("<h3>Render test</h3>"))
```

**Interpret the result:**
- If the test widget/plot also doesn't render: the problem is the IDE or kernel, not the code. Check:
  - Did the IDE (VS Code, Cursor, JupyterLab) recently update?
  - Is `ipywidgets` installed in the active kernel? (`python -c "import ipywidgets; print(ipywidgets.__version__)"`)
  - Try a different kernel or run the notebook in the browser (`jupyter notebook`)
  - For VS Code/Cursor: check that the Jupyter and ipywidgets renderer extensions are installed and enabled
- If the test renders fine: the problem is in the specific cell's code. Proceed to Phase 3.

**Common Cursor/VS Code gotcha:** Editor updates can silently break ipywidgets rendering across all notebooks and all kernels. If ALL widgets fail on ALL kernels, it's almost certainly the editor, not the code.

### 2B: Kernel / Environment Test (for import errors, missing functions, or hangs)

```python
import sys
print(sys.executable)  # Which Python is actually running?
print(sys.prefix)      # Which venv?
```

Then test the specific package:
```python
import the_package
print(the_package.__version__)
print(dir(the_package))  # Does the expected function/class exist?
```

**Common causes:**
- Wrong kernel selected (check kernel picker in top-right of IDE)
- Package installed in one venv but notebook running in another
- Editable install (`pip install -e`) is stale — the source changed but the package wasn't reinstalled
- `%autoreload 2` is loaded but the change requires a kernel restart (e.g., new class, changed `__init__.py` exports)

### 2C: Cell State Test (for NameError or stale values)

```python
# Check if key variables exist and have expected types
for name in ['var1', 'var2', 'var3']:  # Replace with actual variable names
    if name in dir():
        obj = eval(name)
        print(f"{name}: {type(obj).__name__}, {getattr(obj, 'shape', len(obj) if hasattr(obj, '__len__') else '?')}")
    else:
        print(f"{name}: NOT DEFINED")
```

**Common causes:**
- Cells run out of order (cell 5 depends on cell 3, but cell 3 wasn't re-run after a kernel restart)
- Variable was overwritten by a later cell during a previous run, then cells were re-run in a different order
- Kernel was restarted but not all cells were re-run

**Fix:** Kernel > Restart and Run All. If that fixes it, the code is fine — it was cell ordering.

### 2D: Data Pipeline Test (for empty results)

When a cell runs but produces empty output (empty DataFrame, no plot data, "0 results"):

```python
# Check the key variables feeding into the failing cell
print(f"df shape: {df.shape}")
print(f"df columns: {list(df.columns)}")
print(f"df dtypes:\n{df.dtypes}")
print(f"df head:\n{df.head()}")
```

Then check the filter chain step by step:
```python
# Break the filter into individual conditions and count matches
mask1 = df["col1"] == value1
mask2 = df["col2"] >= value2
mask3 = df["col3"].isin(some_list)
print(f"mask1 (col1 == {value1}): {mask1.sum()}")
print(f"mask1 & mask2: {(mask1 & mask2).sum()}")
print(f"mask1 & mask2 & mask3: {(mask1 & mask2 & mask3).sum()}")
```

**Common causes:**
- Filter uses hardcoded dates or thresholds that have expired (e.g., `>= current_month` when the data is from last month)
- Column dtype mismatch — comparing string to int, or datetime to string
- Column was renamed upstream (e.g., after a package update that changed output column names)
- Upstream cell produced data but a filter in between reduced it to zero rows

### 2E: Code Logic Test (for wrong results)

Isolate the smallest reproducible case:

```python
# Pick ONE specific input case and trace it through the function
test_input = df.iloc[0]  # or a known specific case
print(f"Input: {test_input}")
result = the_function(test_input)
print(f"Output: {result}")
print(f"Expected: ...")
```

Then step through the function internals with print statements or by calling sub-steps individually.

## Phase 3: Bisect Within the Layer

Once you know which layer the problem is in, narrow down:

### For rendering problems (layer 1):
1. Does a simple widget work? (tested in 2A)
2. Does this specific widget type work? (e.g., `widgets.Output()` vs `widgets.IntSlider`)
3. Does it work with a single widget or only fail with many? (loop vs single call)
4. Does it work in browser Jupyter but not the IDE?

### For data pipeline problems (layer 4):
1. Which cell in the pipeline first produces empty/wrong data?
2. Walk backward from the failing cell, checking each intermediate variable
3. Print `.shape` and `.head()` at each step

### For code logic problems (layer 5):
1. Does the function work when called directly outside its usual context? (e.g., outside a widget, outside a loop)
2. Does it work with one specific input but not another?
3. Add intermediate `print()` statements inside the function

## Phase 4: Report

Summarize to the user:

1. **Layer:** Which layer the problem was in
2. **Root cause:** What specifically was wrong
3. **Fix:** What to do about it (or whether it's outside our control, like an IDE update)
4. **Workaround:** If the root cause can't be fixed immediately, suggest an alternative approach

## Common Notebook-Specific Gotchas

These are patterns that frequently cause confusion in notebook debugging:

- **`widgets.Output()` swallows exceptions.** Code inside `with out:` that raises an error will capture the error into the widget output — if the widget isn't rendering, you'll never see the error. Test the same code outside the `with out:` block.
- **`%matplotlib inline` vs `%matplotlib widget`.** Wrong backend = plots either don't show or show in wrong place. Check which magic is active.
- **External file edits to `.ipynb` break VS Code.** Editing the raw JSON of a notebook while the IDE has it open can corrupt the IDE's view. Symptoms: can't save, widgets don't render, outputs disappear. Fix: close the notebook in the IDE, verify the file on disk is correct, reopen.
- **Multiple display() calls in a loop.** Each `display()` creates a separate output element. Many widgets in one cell can overwhelm the renderer. Consolidate: `display(widget1, widget2, widget3)` instead of three separate calls.
- **Stale `_month >= current_month` filters.** Notebooks written last month with "future only" filters will show empty results this month if the data hasn't been refreshed. The filter isn't wrong — the data is stale. Re-run the data loading cell.
