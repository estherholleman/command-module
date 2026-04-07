# Design Principles Reference

A medium-agnostic reference for graphic design fundamentals. Applies equally to presentation slides, PDF layouts, web pages, posters, dashboards, and print materials. Organized by discipline, each section covers what to look for, what good looks like, and common failures.

---

## 1. Typography

### Hierarchy

Every visual surface has a reading order. Typography creates it through size, weight, and style contrast.

- **Three levels minimum**: title, subtitle/section, body. Each level must be visually distinct without relying on color alone.
- **Size ratio**: Adjacent levels need enough contrast to be instantly distinguishable. A 1.2x ratio between levels is the minimum; 1.5x-2x reads more confidently. If you have to study which text is the heading, the hierarchy has failed.
- **Weight contrast**: Bold vs. regular is a stronger signal than size alone. A bold 18px heading over regular 16px body is clearer than light 20px over light 16px.
- **Don't use all the tools at once**: If size creates the hierarchy, adding bold + italic + underline + color to the same heading is noise. One or two differentiators per level.

### Font Selection and Pairing

- **One typeface can work**. A single font family with enough weight variation (light, regular, semibold, bold) handles most projects. Two typefaces is the practical maximum for most work.
- **Pair by contrast, not similarity**: A serif headline with a sans-serif body works because they're different jobs. Two similar sans-serifs fight each other.
- **Match the tone to the content**: A startup pitch deck and a government policy report need different typographic voices. Geometric sans-serifs (Futura, Avenir) feel modern and clean. Humanist sans-serifs (Gill Sans, Frutiger) feel approachable. Transitional serifs (Times, Georgia) feel authoritative. Slab serifs (Rockwell, Clarendon) feel bold and grounded.
- **Avoid the defaults**: If the first five people who open the tool would get the same font, pick something else. Calibri, Arial, Times New Roman — these signal "I didn't make a choice." That's fine for internal emails, not for anything meant to persuade or impress.

### Readability

- **Line length (measure)**: 45-75 characters per line for body text. Shorter for slides (where text should be minimal anyway). Longer lines cause the eye to lose its place returning to the left margin.
- **Line height (leading)**: 1.3x-1.6x the font size for body text. Tighter for headings (1.1x-1.2x). Too tight makes text feel cramped; too loose makes lines feel disconnected.
- **Letter spacing (tracking)**: Body text at default. Headings in all-caps need increased tracking (+2-5%). Large display text can go tighter. Never tighten body text tracking.
- **Alignment**: Left-aligned is the default and safest choice. Centered works for short text (titles, labels, invitations) but breaks down beyond 2-3 lines. Justified needs careful hyphenation to avoid rivers of white space. Right-aligned has narrow use cases (dates, numbers in tables, design accent).

### Common Typography Failures

- Too many font sizes with no clear hierarchy (the "font size soup" problem)
- Tiny text to fit more content — if it doesn't fit, cut the content
- Decorative fonts for body text
- All-caps body text (shouting, hard to read)
- Inconsistent font usage across slides/pages — same role should always get the same treatment

---

## 2. Color

### Theory and Harmony

Color harmony isn't decoration — it's how you make a visual surface feel coherent rather than random.

- **Monochromatic**: One hue, varied by saturation and lightness. Hard to get wrong, easy to make boring. Works well for data-heavy or professional contexts.
- **Analogous**: 2-3 adjacent hues on the color wheel (blue, blue-green, green). Feels natural and harmonious. Needs one dominant hue; the others support.
- **Complementary**: Opposite hues (blue/orange, red/green). High energy, high contrast. Use one as dominant, the other as accent only — 80/20 or 90/10 split. Equal amounts of complementary colors vibrate and fight.
- **Split-complementary**: One hue plus the two neighbors of its complement. Easier to work with than direct complements, still lively.
- **Triadic**: Three evenly spaced hues. Vibrant but hard to balance. Usually needs one dominant, two accents.

### Building a Palette

- **Start with one color**. The brand color, the mood color, or the dominant image's color. Everything else follows from it.
- **Add neutrals first**: Most of your palette should be neutral — whites, grays, near-blacks, or warm/cool-tinted neutrals. Color is the accent, not the base.
- **One accent, maybe two**: A single strong accent color is almost always enough. A second accent should serve a different function (e.g., interactive elements vs. alerts).
- **Saturation consistency**: Colors in the same palette should share a saturation range. A fully saturated red next to a muted sage green looks accidental, not designed.
- **Temperature matters**: Warm palettes (red, orange, yellow undertones) feel energetic and inviting. Cool palettes (blue, green, purple undertones) feel calm and professional. Mixing temperatures intentionally creates tension; mixing them accidentally creates confusion.

### Contrast and Accessibility

- **Text contrast**: Body text needs at minimum a 4.5:1 contrast ratio against its background (WCAG AA). Large text (18px+ or 14px+ bold) needs 3:1. This isn't optional — it's readability.
- **Don't rely on color alone**: If red means "bad" and green means "good," colorblind users see two grays. Pair color with shape, icon, label, or position.
- **Light text on dark backgrounds**: Needs more weight or size than dark text on light backgrounds. Thin white text on dark backgrounds is a common readability failure.

### Common Color Failures

- Too many colors with no clear role for each — the "rainbow" problem
- Low contrast text that's unreadable on its background
- Background colors that compete with content instead of supporting it
- Gradients that make text partially readable and partially not
- Red and green as the only differentiators (colorblind-hostile)
- Pure black (#000) on pure white (#FFF) — harsh. Use near-black (#1a1a1a, #222) for a softer feel
- Inconsistent color use — the same color meaning different things on different pages/slides

---

## 3. Composition and Layout

### Visual Weight and Balance

Every element on a surface has visual weight — determined by size, color intensity, contrast, density, and position. Balance is how those weights are distributed.

- **Symmetrical balance**: Equal weight on both sides of a center axis. Feels formal, stable, predictable. Good for certificates, invitations, serious institutional work.
- **Asymmetrical balance**: Unequal distribution that still feels stable. A large light element balanced by a small dark element. More dynamic, more interesting, harder to execute.
- **Intentional imbalance**: Breaking balance on purpose creates tension and draws the eye. But it should look deliberate, not accidental.

### Alignment

- **Everything should align to something**. If an element looks like it's "almost" aligned but not quite, it reads as a mistake. Either align it or move it far enough away that the offset is clearly intentional.
- **Invisible grid**: Even when not using an explicit grid, elements should snap to implied vertical and horizontal lines. Check: if you drew lines extending from the edges of your elements, would they connect to other elements?
- **Edge alignment over center alignment**: Left-aligning text blocks to a shared left edge creates a strong vertical line that organizes the page. Center-aligning multiple elements at different widths creates a ragged edge on both sides.

### Proximity and Grouping

- **Related things go together**: Elements that belong to the same logical group should be visually close. The space between them should be noticeably less than the space separating them from other groups.
- **White space is structure**: Space isn't "empty" — it's what defines the groups. The ratio between inner spacing (within groups) and outer spacing (between groups) should be at least 2:1, preferably 3:1 or more.
- **If everything is equally spaced, nothing is grouped**: A grid of identically-spaced items with no grouping reads as a list, not a structure. Add spacing hierarchy.

### The Grid

- **Grids exist to create rhythm and consistency**, not to fill every cell. Columns, gutters, and margins define the structure; content occupies it selectively.
- **Modular scale for spacing**: Pick a base unit (4px, 8px, or a proportional unit) and derive all spacing from multiples of it. 8, 16, 24, 32, 48, 64 — not 8, 13, 22, 37.
- **Margins matter**: Content that touches or nearly touches the edge of its container feels cramped. Generous margins signal confidence and quality.

### Common Composition Failures

- Elements that are "almost" aligned but not quite — nothing looks more amateur
- Equal spacing everywhere with no visual grouping
- Content crammed to the edges with insufficient margins
- Too many focal points competing for attention (if everything is bold, nothing is)
- Centered layouts with ragged edges on both sides
- Slide layouts that change structure randomly from slide to slide

---

## 4. Visual Hierarchy

How the eye moves through a visual surface. Typography, color, size, position, and white space all contribute, but hierarchy is the combined effect.

### Creating Reading Order

- **Size is the strongest signal**: The largest element gets attention first. Always.
- **Position matters**: Top-left in LTR cultures, top-right in RTL. Elements above the fold / above the midline get seen before elements below.
- **Contrast draws the eye**: A bright element on a muted background, a dark element on a light background, a saturated color among neutrals.
- **Isolation amplifies importance**: An element surrounded by white space gets more attention than one crowded by neighbors.
- **Direction and flow**: Lines, arrows, the gaze of photographed faces, and the shape of whitespace all guide the eye through the composition.

### The Squint Test

Blur your vision or step back from the screen. What you notice first is what your audience will notice first. If the answer is wrong (a decorative element instead of the main message), the hierarchy needs work.

### Information Density

- **Slides**: Minimal information per surface. One idea per slide. If a slide needs more than 30 seconds to absorb, it has too much.
- **Dashboards**: Dense is fine, but not undifferentiated. Create zones of importance. Primary metrics large and prominent; secondary metrics smaller; tertiary details available on demand.
- **Documents**: Body text can be dense; but section breaks, pull quotes, figures, and white space create pacing and rest points.
- **Posters**: One dominant visual, one dominant message. Everything else is supporting.

### Common Hierarchy Failures

- No clear primary element — the eye bounces without landing
- Decorative elements (backgrounds, borders, icons) competing with content
- Every bullet point the same size and weight — a flat list where some points matter more than others
- Headers that are only slightly larger than body text, failing the squint test
- Important information buried in the visual middle ground

---

## 5. White Space

Not "empty space" — it's a structural design element with its own purpose.

### Types

- **Macro white space**: The big gaps — margins, space between sections, header-to-content distance. Defines the overall feel: generous macro space signals quality, authority, and confidence.
- **Micro white space**: The small gaps — line height, letter spacing, padding inside buttons, space between an icon and its label. Defines readability and comfort.

### Principles

- **White space is not wasted space**: The impulse to fill every gap is the single most common design failure in non-designer work. Resist it.
- **More white space almost always improves non-expert work**: If someone who isn't a designer made it, adding 50% more white space will almost certainly make it better.
- **Asymmetric white space creates direction**: More space on one side of an element makes it feel like it belongs to whatever is on the other side.
- **Consistent white space creates rhythm**: Inconsistent spacing (15px here, 23px there, 8px somewhere else) creates subconscious discomfort even when people can't articulate why.

### Common White Space Failures

- Slides crammed with text leaving no breathing room
- Content that touches or nearly touches container edges
- Inconsistent spacing that creates a "messy desk" feel
- Using borders/lines to separate things that could be separated by space alone
- Filling silence — adding decorative elements to "empty" areas

---

## 6. Gestalt Principles

How humans perceive visual groups and patterns. These operate below conscious awareness and override explicit labels.

- **Proximity**: Things near each other are perceived as related. The most powerful grouping principle — stronger than color, shape, or enclosure.
- **Similarity**: Things that look alike (same color, shape, size) are perceived as related. Useful for indicating category membership.
- **Continuity**: The eye follows lines, curves, and implied directions. A row of dots is perceived as a line, not individual dots.
- **Closure**: The mind fills in gaps to complete familiar shapes. Logos and icons exploit this — you don't need to draw every line.
- **Figure/Ground**: The brain separates foreground from background. Ambiguous figure/ground relationships create visual confusion (or intentional optical illusions).
- **Common region**: Elements within a shared boundary (box, background color, bordered area) are perceived as grouped. Cards work because of this principle.

### Applying Gestalt

- Use proximity before enclosure. Moving related items closer together is more elegant than putting a box around them.
- When alignment, proximity, and similarity all agree, the grouping is unambiguous. When they contradict each other, the design feels wrong even if each element individually is fine.
- Test: can someone who doesn't read the language still understand the structure? If the visual grouping is strong enough, yes.

---

## 7. Presentation-Specific Principles

Slides are a distinct medium with their own rules. They're projected, viewed from a distance, time-constrained, and support a spoken narrative.

### Content

- **One idea per slide**. If you need a second idea, make a second slide.
- **Text is not the presentation — you are**. Slides support the speaker, not replace them. If the slides make sense without narration, they have too much text.
- **Maximum ~6 lines of text, ~6 words per line** (the "6x6 rule" as a rough ceiling, not a target). Fewer is better.
- **Headlines, not sentences**: "Revenue grew 40% YoY" is a headline. "In Q3 2025, our company's revenue grew by approximately 40% year-over-year, driven primarily by expansion in the Asian market" is a paragraph that belongs in a document, not a slide.

### Visual Treatment

- **Contrast for projection**: Room lighting washes out subtlety. Colors that work on your laptop monitor may be invisible projected. Use high contrast.
- **Font size floor**: Nothing below 24px for body text, nothing below 36px for headlines. If it doesn't fit at those sizes, it doesn't fit on the slide.
- **One dominant visual per slide**: A single image, chart, or diagram. Not three small images competing with each other.
- **Full-bleed images**: An image that fills the entire slide background is almost always stronger than a small image floating in white space. Overlay text on a calm region.
- **Consistent template**: Every slide should feel like it belongs to the same deck. Same margins, same font treatment, same color usage. Variation in layout is fine; variation in visual language is not.

### Data Visualization on Slides

- **Label directly**, not with legends. Put the label on or next to the data, not in a separate box the viewer has to cross-reference.
- **Highlight what matters**: If one bar in a bar chart is the point, color it differently. Don't make the audience search for the insight.
- **Round numbers for slides**: "~40%" is better than "39.7%" in a presentation. Precision matters in reports, not talks.
- **One chart, one point**: If a chart supports multiple arguments, show it multiple times with different highlights, not once with everything highlighted.

### Transitions and Animation

- **Transitions between slides**: Simple and consistent. Fade or cut. Dissolve is acceptable. Everything else (swipe, zoom, rotate, bounce) distracts from the content.
- **Build animations** (revealing bullet points one at a time): Useful when each point needs individual discussion. Unnecessary when the audience will read the whole slide anyway.
- **Motion should be invisible**: Good animation feels like a natural part of the narrative flow. If the audience notices the animation itself, it's too much.

---

## 8. Critique Framework

When evaluating any visual artifact, work through these questions in order.

### First Impression (2-second test)

- What do you notice first? Is that the right thing to notice first?
- Does the overall composition feel balanced or lopsided?
- Does it feel professional or amateur? What's creating that feeling?

### Hierarchy (10-second test)

- Can you identify the primary message/element without reading?
- Is there a clear reading order: first this, then this, then this?
- Does the squint test confirm the intended hierarchy?

### Structure

- Is there an underlying grid or alignment system?
- Are related elements grouped by proximity?
- Is the spacing consistent and purposeful?
- Is white space used as structure, or is it accidentally leftover?

### Typography

- Are there clear typographic levels?
- Is the type readable at intended viewing distance?
- Are font choices appropriate for the content and audience?
- Is type usage consistent throughout?

### Color

- Does the palette have a clear logic (one dominant + neutrals + accent)?
- Is contrast sufficient for readability?
- Does color serve a purpose (hierarchy, grouping, meaning) or is it decoration?
- Would this work for someone who is colorblind?

### Medium-Specific

- Apply the presentation, document, dashboard, or poster-specific criteria as relevant
- Consider the viewing context: projected? phone? print? monitor?

### Overall Coherence

- Do all elements feel like they belong to the same design?
- Is there a consistent visual language (same border-radius, same shadow style, same spacing scale)?
- Could you describe the design's "voice" in one sentence?
