
## More Critical Lessons (from Page 73 rebuild)

### Elementor Frontend Rendering
- After writing `_elementor_data` directly to DB, the frontend won't render until:
  1. Use `elementor_canvas` template (NOT "default")
  2. Open the page in Elementor editor and **save/publish** once - this triggers CSS generation
  3. Without this, the page will show blank (canvas) or just the title (default template)

### Working Recipe for Programmatic Elementor Pages
1. Create page with post_status="publish"
2. Write `_elementor_template_type` = "wp-page"
3. Write `_elementor_data` = valid JSON array of containers/sections
4. Write `_wp_page_template` = "elementor_canvas"
5. **DO NOT** write `_elementor_page_settings` 
6. **DO NOT** write `_elementor_css` 
7. Open Elementor editor and save once to generate CSS

### Site Info (Corrected)
- Actual WordPress: `D:\wordpress\site` (NOT D:\建站\one\one\app\public)
- Apache: XAMPP at `C:\xampp\`, runs as Windows service (apache-xampp)
- MySQL: XAMPP at port 3306, user=wp_user, password=wp_password123
- Site URL: http://wordpress.local
- DB name: wordpress_db, prefix: wp_
- Theme: Twenty Twenty-Five



## New Lessons from Page 73 Rebuild (2026-06-05)

### 1. Font Size / Typography
- Issue: Heading widget typography lost - CSS not generated
- Fix: Use text-editor with inline h2 style
- Root cause: Elementor compiles typography into post-CSS file

### 2. Icons / Unicode Chars
- Issue: Raw Unicode chars show as ?
- Fix: Use HTML entities instead of raw Unicode
- Root cause: UTF-8 corrupted through PHP/MySQL encoding

### 3. Column Wrapping on Desktop
- Issue: Columns over 100% total width do not wrap on desktop
- Fix: Each section columns must total exactly 100%
- Root cause: Elementor CSS wraps only on tablet (<1024px)

### 4. Settings Stripped by save()
- Issue: gap, content_width, style tags stripped after CSS regeneration
- Fix: Never call document->save(). CSS-only regeneration only.
- Root cause: save() triggers Elementor sanitization

### 5. Hover Animations
- Issue: Custom divs or style tags stripped
- Fix: Use Elementor custom_css setting on columns
- Note: custom_css compiles into post CSS properly

### 6. Column Gap
- Issue: gap setting stripped from legacy sections
- Fix: Set gap=no, control via column padding

### 7. Preferred Types
- Use: legacy section + column (reliable)
- Avoid: flex container type (complex)
- Widget: text-editor over heading/image
- Icon: HTML entities over SVG over Unicode over Font Awesome

### 8. Verification Checklist
- Rendered HTML has correct content
- CSS file (post-73.css) has custom styles
- Gap/column classes correct
- Icons render (not question marks)
- Hover animations work
- Page status = publish
- CSS file loaded in page

### 9. Container Type Does NOT Generate Width CSS
- Issue: Container children with 50% inline_size render as 100% width (stacked)
- Root cause: CSS generator does not compile inline_size into CSS for containers via direct DB
- Detection: Check post-73.css for --width rules. If only --display:flex, containers stack.
- Fix: Use legacy section + column type (generates elementor-col-XX classes from frontend.css)

### 10. Legacy Section + Column is More Reliable for Direct DB Writes
- Legacy sections generate proper column width CSS
- Container type relies on CSS variables that require proper CSS generation
- For direct DB writes: ALWAYS use section+column, NEVER container type
- Column widths must add up to exactly 100% to avoid flex-wrap issues

### 11. Container vs Section Decision Matrix
- Width: Section(col-XX works) > Container(--width broken via DB)
- Gap: Section(broken by save()) < Container(works)
- flex-wrap: Section(tablet only) < Container(flex_wrap works)
- Direct DB: Section(RECOMMENDED) > Container(NOT recommended)


### 12. 2-Column Layout Not Rendering (Legacy Section)
- After rebuilding Section 1 with legacy section + 2 columns at 50%, columns STILL stacked vertically
- Root cause 1: Elementor CSS has flex-wrap:wrap only on tablet. Desktop defaults to nowrap
- Root cause 2: Even with 50%+50%=100%, some CSS cascade issue prevented side-by-side display
- Fix: Add custom_css to the SECTION settings:
  'settings': { 'custom_css': '.elementor-container{flex-wrap:wrap!important;}.elementor-column{width:50%!important;}' }
- This gets compiled into post CSS by CSS generator and STAYS after regeneration
- Alternative: Append to post CSS file after generation (gets overwritten on next regen - NOT reliable)

### 13. Verification Checklist (Expanded)
- [ ] DB data has correct element types and column sizes
- [ ] Rendered HTML has correct column classes (elementor-col-XX)
- [ ] CSS file (post-73.css) has generated custom styles
- [ ] CSS file has flex-wrap rules if section sums to exactly 100%
- [ ] Page status is publish
- [ ] ACTUALLY CHECK the frontend in a browser (not just server-side)

### 14. custom_css Does NOT Work on Nested Container Children
- Issue: Added custom_css to container-type children (cards), but CSS was NOT generated in post-73.css
- Root cause: Elementor CSS generator processes custom_css only for top-level containers/sections and widgets. Nested containers' custom_css is ignored.
- Detection: Check generated CSS file for the rule after regeneration. If missing, custom_css was ignored.
- Fix: Restructure to avoid nested containers. Use multiple legacy sections instead, each with columns totaling exactly 100%.

### 15. When to Use Container vs Section Type (Updated)
| Use Case | Recommended Type |
|----------|----------------|
| Simple row of columns | Legacy section + column |
| Nested layouts with inner containers | Multiple legacy sections |
| Hover animations | Section/column with custom_css (selector works) |
| column_gap / flex_wrap | Container type (supports these settings) |
| Width control via direct DB | Legacy section (elementor-col-XX classes work) |

### 16. Column Gap (Left-Right Spacing) in Legacy Sections
- Issue: Elementor column-gap-XX adds INNER padding to .elementor-element-populated, not outer margin between columns. Cards appear flush/touching even with gap set.
- Root cause: gap padding is INSIDE the column's background area, not BETWEEN columns
- Fix: Add custom_css to each column: 'custom_css': 'selector{margin:0 8px; width:calc(50% - 16px)!important;}'
- For 4-column layout (25% each): margin:0 6px; width:calc(25% - 12px)
- Important: custom_css on legacy section COLUMNS works (CSS generator compiles it). Does NOT work on nested container children.

### 17. Making Cards Smaller
- Reduce text-editor padding: 20px 24px -> 14px 18px or 12px 16px
- Reduce font sizes: h3 from 1.1rem to 0.95-1rem, body from 0.9rem to 0.85rem
- Feature list padding: 4px -> 3px, font-size: 0.87rem -> 0.82-0.85rem
- Image border-radius: keep 8px 8px 0 0 (flat bottom for modern card look)
- Column padding: reduce from 36px 24px to smaller values

### 18. Section 3 (4 Cards) Left-Right Spacing + Resize
- Issue: 4 cards stacked vertically initially (container type), then horizontal but touching/too large after legacy section fix
- Root cause of left-right spacing: column gap/padding adds inner padding, not outer margin between cards
- Fix: custom_css on each column -> selector{margin:0 6px; width:calc(25% - 12px)!important;}
- For smaller cards: reduce icon size (56px→44px), icon font-size (26px→22px), title (1.2rem→1rem), description (0.88rem→0.85rem)
- Decrease column padding: 32px→24px (top/bottom), 24px→12px (left/right)
- Verification: check that width:calc values are present in post-73.css after regeneration

### 19. Self-Detection Patterns for Common Issues
- **Layout flattening (multi-col→single col)**:
  1. Check DB: element_type = "section" and columns have correct width/margin settings
  2. Check HTML: .elementor-section and .elementor-column classes present
  3. Check CSS: post-73.css has the custom_styles and column width rules
  4. View source: inspect rendered HTML for flex-wrap and column width values
- **Missing icons**: Verify HTML entities (e.g. \u0026#9889;) not garbled by JSON serialization → use raw string &#9889; in Python
- **CSS not applying**: custom_css on nested container children is IGNORED by CSS generator. Only works on top-level section/container and widget-level settings
- **Card touching** = missing margin between columns. Fix: custom_css with calc() width. Verify in frontend, not just DB
- **Font size not changing**: heading widget typography settings don't generate CSS. Use text-editor with inline styles instead

### 20. Hover Effects ≠ Entrance Animations
- _animation setting (fadeInUp, fadeIn) = entrance animation, triggered by JS on scroll → adds elementor-invisible class (hides element until triggered)
- Hover effects = CSS :hover pseudo-class (transform, box-shadow change)
- For hover effects on legacy section columns, use custom_css: 'selector{transition:all 0.3s ease;}selector:hover{transform:translateY(-4px);box-shadow:0 8px 30px rgba(...)}'
- Entrance animations with _animation can cause cards to stay invisible if JS doesn't trigger (elementor-invisible with no animation class added)

### 21. Merging Sections & Re-indexing
- When merging two sections (e.g. 2 rows of 2 cards → 1 row of 4 cards), remember:
  - Pop() removes the section and shifts all subsequent indices
  - After merge, all downstream indices in the data array are shifted by 1
  - Verifying frontend HTML shows updated column classes (elementor-col-25)
- For 4 columns side by side: each column gets _column_size=25 + custom_css margin + calc(25% - 12px)

### 22. Self-Check Patterns for Card Layout Issues
- **Cards stack vertically**: check flex-wrap on section container → add '.elementor-container{flex-wrap:wrap!important;}' to section custom_css
- **Cards touching/flush**: check margin on columns → add 'selector{margin:0 Xpx; width:calc(Y% - 2Xpx)!important;}'
- **Cards invisible/blank**: check for elementor-invisible class → remove _animation setting, use CSS keyframes instead
- **Content exists in DB but not on page**: check if section is container type (not recommended for direct DB writes) → convert to legacy section
- **CSS not generated**: custom_css on nested container children is IGNORED. Only works on top-level sections and columns.

### 23. Title + Cards Must Be in the Same Section
- Issue: Title and cards were split into two separate Elementor sections (title section + cards section)
- Demo pattern: Title, subtitle, and cards are all inside ONE <section> element
- Fix: Put title as first column (100% width) and cards as remaining columns (25% or 33.33%) in the SAME section
- Key: Add flex-wrap:wrap to section's custom_css so the 100% title column wraps to its own line and cards wrap below
- Correct structure:
  `
  Section {flex-wrap:wrap}
    ├── Col 1: _column_size=100 → title (takes full width, wraps)
    ├── Col 2: _column_size=25 → card 1 (wraps to next line)
    ├── Col 3: _column_size=25 → card 2
    ├── Col 4: _column_size=25 → card 3
    └── Col 5: _column_size=25 → card 4
  `

### 24. Card Width Must Account for Margin via calc()
- Issue: Cards with margin but without calc() in width → total width exceeds 100% → cards wrap to next line
- Root cause: elementor-col-XX sets width to XX% but margin is ADDED on top, so 4 × (25% + 16px) > 100%
- Fix: Always use calc() when adding margin:
  - margin:0 6px → width:calc(25% - 12px)!important (6px × 2 = 12px)
  - margin:0 8px → width:calc(25% - 16px)!important (8px × 2 = 16px)
  - margin:0 8px → width:calc(33.33% - 16px)!important
- Detection: Check rendered page for cards wrapping to next row → check custom_css for missing width:calc()

### 25. Post Status Can Change to 'future' During CSS Regeneration
- Issue: After CSS regeneration, post 73's status changed from 'publish' to 'future' → page shows empty
- Detection: Page HTML has NO elementor-section elements despite data being in DB
- Fix: ALWAYS verify post_status after any DB operation: UPDATE wp_posts SET post_status='publish' WHERE ID=73
- Root cause: The regenerate_css.php or Elementor's save process may set post_status to 'future' when triggered without a user session
- Prevention: Add post_status check to the verification checklist

### 26. Self-Check Verification Checklist (Final Version)
1. [ ] DB data has correct element types, column sizes, and custom_css
2. [ ] Post status is 'publish' (not 'future' or 'draft')
3. [ ] Rendered HTML has correct number of elementor-section elements
4. [ ] Rendered HTML has correct column classes (elementor-col-XX)
5. [ ] Cards are in the SAME section as the title (not split across sections)
6. [ ] CSS file (post-73.css) has:
   - flex-wrap:wrap rules for sections with multi-row layouts
   - calc() width rules for cards with margins
   - hover effects (:hover rules)
7. [ ] Card widths with margin = width:calc(XX% - 2*MARGINpx)!important
8. [ ] Content verification: ALL key text strings appear in rendered HTML
9. [ ] ACTUALLY CHECK the frontend in a browser (CSS hover, layout, images)

### 23. Button Background-color Not Compiled (2026-06-05)
- Issue: Elementor CSS generator does NOT compile `button_background_color` into post CSS
- Detection: Buttons appear transparent/outline-only in frontend, missing their fill color
- Fix: Add inline `<style>` in an HTML widget with `!important` rules for ALL button background colors
- Example:
  ```css
  .elementor-94 .elementor-element.elementor-element-hero-btn .elementor-button{background-color:#FFFFFF!important}
  .elementor-94 .elementor-element.elementor-element-s2-btn .elementor-button{background-color:#0D484C!important}
  .elementor-94 .elementor-element.elementor-element-s4-btn .elementor-button{background-color:#45CCD6!important}
  ```
- Note: Both normal state AND hover state `background-color` need `!important`. Hover colors can be added to the same inline style block.

### 24. Script Tag Must Use `</script>` Not `<\/script>` (2026-06-05)
- Issue: When storing JavaScript in an HTML widget via direct DB write, `<\/script>` is NOT recognized by the browser as the script closing tag
- Root cause: In HTML parsing, only `</script>` (no backslash) closes a `<script>` element. `<\/script>` is treated as content
- Detection: FAQ accordion, custom JS, or any inline script silently fails to execute
- Fix: Ensure the closing tag is exactly `</script>` (no `\/` escaping)
- Special note: When writing PHP strings for inline scripts, use `</script>` directly. With `JSON_UNESCAPED_SLASHES`, the forward slash is preserved correctly in the database.

### 25. IIFE Must Be Invoked With `()` (2026-06-05)
- Issue: `(function(){...});` defines a function but never executes it
- Detection: Self-executing function code runs silently; no click handlers or DOM changes take effect
- Fix: Always use `(function(){...})();` — the trailing `()` is required for immediate invocation
- Note: The `});` vs `})();` distinction is critical. Without `()`, the function expression is parsed but never called.

### 26. Unicode Escapes: PHP vs JSON Handling (2026-06-05)
- Issue: PHP strings containing `\uXXXX` (e.g. `\u00b0` for °) are NOT interpreted as Unicode by PHP — they remain literal 6-character sequences
- When `json_encode` processes these, it escapes the backslash, resulting in `\\u00b0` in the JSON string (double-escaped)
- In the frontend, Elementor renders the literal text `\u00b0` instead of `°`
- Fix: Before writing to DB, replace `\\uXXXX` patterns with actual UTF-8 characters using `preg_replace_callback`
- For supplementary Unicode (emoji): `\U0001XXXX` (8 hex digits) must be handled separately with UTF-8 surrogate pair encoding
- Use `JSON_UNESCAPED_UNICODE` flag in `json_encode` to keep UTF-8 characters as-is

### 27. Verification Checklist (Updated 2026-06-05)
Add these checks after every DB write + CSS regeneration:
1. [ ] Buttons have visible background color (not transparent outline)
2. [ ] Custom `<script>` tags use `</script>` (no backslash) and execute correctly
3. [ ] IIFE/self-executing functions have `()` invocation at the end
4. [ ] All Unicode characters (degree symbols, arrows, emoji) render as proper glyphs, not escaped text
5. [ ] CSS file contains ALL expected rules — check button background-color specifically

## New Lessons from Page 94 eCall Battery Rebuild (2026-06-05)

### 28. Broken Container Section Causes Fatal Error
- Issue: A `container` type element at index 0 with `elements: [{elements: null}]` caused: `Fatal error: Uncaught TypeError: ElementorPro\Modules\GlobalWidget\Module::get_element_child_type()`
- Detection: Page returns ~4700 bytes with error instead of full Elementor page
- Fix: Remove the broken section from the array and re-index:
  ```php
  array_shift($decoded); // Remove section 0
  $decoded = array_values($decoded); // Re-index
  ```
- Note: Always verify the page loads after removal (check for 90K+ byte response)

### 29. PowerShell PHP Script Writing — Smart Quote Pitfall
- Issue: When writing PHP code inside PowerShell `@'...'@` heredoc, single quotes `'` followed by `)` (like `meta_key="_elementor_data'")`) get converted to Unicode smart quotes by PowerShell
- Result: PHP parses them differently, causing `Parse error: syntax error, unexpected single-quoted string`
- Fix options:
  - Use `"` double quotes in PHP: `$meta = $wpdb->get_var('SELECT ... AND meta_key="_elementor_data"');`
  - Or use `[System.Text.Encoding]::UTF8.GetBytes(@'...'@)` and `[System.IO.File]::WriteAllBytes()` to avoid string processing
  - Or write simple scripts that avoid `'_elementor_data'"` patterns

### 30. _elementor_data Can Be Wiped to Empty String
- Issue: A failed PHP execution (syntax error) can write empty string to `_elementor_data` meta field
- Detection: `_elementor_data` shows 0 chars in DB query; page shows no Elementor sections
- Recovery: Check for autosave/revision:
  ```php
  $autosave = $wpdb->get_var("SELECT meta_value FROM wp_postmeta pm JOIN wp_posts p ON pm.post_id=p.ID WHERE p.post_parent=94 AND pm.meta_key='_elementor_data' LIMIT 1");
  ```
- Prevention: Always validate `json_encode` output length before DB write:
  ```php
  if (strlen($new_meta) > 10000) { $wpdb->update(...); }
  ```

### 31. Degree Symbol (°) in PHP Strings — Use Correct Encoding
- Issue: `\u00b0` in PHP double-quoted strings is NOT interpreted as the degree symbol — PHP uses `\u{00b0}` syntax for Unicode
- Result: `json_encode` outputs literal `\u00b0` which browser renders as text, not °
- Fix options:
  - PHP: Use actual UTF-8 byte `"\xc2\xb0"` for degree symbol
  - HTML: Use `&deg;` HTML entity (recommended for Elementor HTML widgets)
  - Emoji: Use raw emoji bytes like `"\xF0\x9F\x93\x9E"` for 📞

### 32. CSS Grid Spacing — gap vs margin on Grid Items
- Issue: Card spacing via CSS Grid `gap` works for between-item spacing but user may delete it when editing
- Fix for card items inside CSS Grid:
  - Use `gap:Xpx` on the grid container for between-item spacing
  - Optionally add `margin:Xpx!important` on each grid item for additional spacing
  - Add section `padding` settings for section-level spacing
- Elementor section padding in data:
  ```php
  $decoded[$idx]["settings"]["padding"] = array(
    "unit" => "px", "top" => "80", "right" => "20", "bottom" => "80", "left" => "20", "isLinked" => false
  );
  ```
- Note: CSS Grid `gap` combined with `margin` on items = extra spacing. Only use one or the other for simplicity.

### 33. Custom Font Installation for Local WordPress
- Issue: Live site uses custom font (e.g., "OPPO Sans") registered via Elementor Pro Custom Fonts, but local instance doesn't have it
- Fix (without Elementor UI):
  1. Download the font file from the live site (check `@font-face` src URL in page source)
  2. Place in `wp-content/uploads/`
  3. Add `@font-face` declaration to the page's inline CSS
  4. Reference the font name in `body{font-family:"FontName",Fallback,sans-serif!important}`
- Example:
  ```php
  $fontface = "@font-face{font-family:'OPPO Sans';font-style:normal;font-weight:normal;src:url('http://wordpress.local/wp-content/uploads/NotoSans-Regular.woff2') format('woff2')}";
  ```
- Note: The font name doesn't need to match the actual font file name — the `@font-face` declaration defines the mapping. Elementor Pro's Custom Fonts feature does this automatically via the admin UI.

### 34. Swap Module Positions in Elementor Data
- To move columns between sections in `_elementor_data`:
  ```php
  // Extract columns from source section
  $cols_to_move = array_slice($decoded[$src_idx]["elements"], $start, $length);
  // Remove from source
  $decoded[$src_idx]["elements"] = array_slice($decoded[$src_idx]["elements"], 0, $start);
  // Add to target section
  $decoded[$target_idx]["elements"] = array_merge($decoded[$target_idx]["elements"], $cols_to_move);
  ```
- Column IDs (`id` field) remain valid even in different sections — Elementor identifies by element ID, not position
- Update section `_element_id` and `id` if the section role changes
