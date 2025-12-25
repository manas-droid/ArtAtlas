# Core Principle (Lock This First)

> **Users should never see a graph.
> They should see a story derived from the graph.**

The Explanation Graph is an **internal representation**.
The UI must present a **linear, readable explanation**.

---

## Step 1 — Decide What the User Is Actually Asking

A general user is not asking:

> “Show me nodes and edges.”

They are asking:

> **“Why am I seeing this artwork?”**
> **“How does this relate to what I searched for?”**

So the UI transformation must answer **those two questions**, clearly.

---

## Step 2 — Collapse the Graph into a Human-Friendly Structure

Your graph already encodes this path:

```
Query
 → Concept
 → Evidence Bundle
 → Artwork
```

So the UI transformation should be:

### 👉 **Concept-first explanation**

That means:

```text
You searched for: “symbolism in still life”

We identified these ideas:
• Vanitas
• Still Life

Here is the visual evidence supporting each idea.
```

---

## Step 3 — UI-Friendly “Explanation Blocks” (Key Abstraction)

Transform the graph into **Explanation Blocks**, one per concept.

### Each Explanation Block contains:

1. **Concept label**
2. **Why this concept was detected**
3. **Which artworks support it**
4. **How strong the evidence is**

---

## Concrete UI Data Shape (Derived from Graph)

From your Explanation Graph, generate:

```json
[
  {
    "concept": {
      "id": 2,
      "label": "Vanitas",
      "confidence": 0.8559
    },
    "evidence_confidence": 0.6636,
    "artworks": [
      {
        "artwork_id": 9245,
        "mapping_confidence": 0.6636,
        "provenance": "embedding_similarity"
      }
    ]
  },
  {
    "concept": {
      "id": 3,
      "label": "Still Life",
      "confidence": 0.8086
    },
    "evidence_confidence": 0.6070,
    "artworks": [
      {
        "artwork_id": 14258,
        "mapping_confidence": 0.6070,
        "provenance": "embedding_similarity"
      }
    ]
  }
]
```

This is **NOT a graph anymore**.
This is a **UI-ready explanation model**.

---

## Step 4 — What the User Actually Sees (Critical)

### Section 1 — Query Acknowledgement

At the top:

> **“Showing results for: *symbolism in still life*”**

Optional subtext:

> “We identified concepts commonly associated with your query.”

---

### Section 2 — Concept Explanation Cards (Main UI)

For each concept:

---

### 🟦 Concept Card: *Vanitas*

**Why this concept appears**

> Detected from your query with high confidence (86%)

**Visual evidence**

> The following artworks support this concept:

🖼 Artwork thumbnail

* *Support strength:* Medium–High (66%)
* *Why:* Visual similarity to known Vanitas works

---

### 🟦 Concept Card: *Still Life*

**Why this concept appears**

> Detected from your query with high confidence (81%)

**Visual evidence**

> The following artworks support this concept:

🖼 Artwork thumbnail

* *Support strength:* Medium (61%)
* *Why:* Visual similarity to Still Life compositions

---

## Step 5 — How to Show Confidence (Very Important)

### Never show raw numbers first

Instead:

| Confidence | Label       |
| ---------- | ----------- |
| ≥ 0.85     | Very strong |
| 0.7–0.85   | Strong      |
| 0.6–0.7    | Moderate    |

You can show numbers **on hover or expand**, not by default.

---

## Step 6 — “Explain More” (Advanced, Optional)

When the user clicks **“Why?”**, you can show:

> “This artwork was linked to *Vanitas* because its visual features closely match known Vanitas compositions.
> (embedding-based similarity)”

That sentence is literally derived from:

```json
provenance = "embedding_similarity"
```

---

## Step 7 — What NOT to Expose in UI

❌ Node IDs
❌ Edge types
❌ Raw graph
❌ Internal thresholds
❌ Validation logic

Those are **engineering artifacts**, not user concepts.

---

## Mental Model to Lock for UI

```
Explanation Graph (internal)
        ↓
Explanation Blocks (structured)
        ↓
Concept Cards + Artwork Evidence (UI)
```

---

## Why This Works for a Demo

* Feels **intelligent**, not technical
* Makes no claims you can’t justify
* Scales to more concepts naturally
* Easy to narrate in a video:

  > “We detect concepts, then show visual evidence for each.”

Recruiters will *get it instantly*.

---

## Next Step (Very Natural)

Now that the **UI transformation model** is clear, the next concrete step is:

👉 **Design a single v3 UI screen**

* layout
* components
* minimal interactions

If you want, next I can:

* sketch the exact screen layout (left / center / right)
* or define React component boundaries

Just tell me how visual you want to go next.
