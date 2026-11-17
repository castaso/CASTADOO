#!/usr/bin/env node
/**
 * Regenerate the CASTADOO brand binaries at their existing upstream paths.
 *
 * This is a RECIPE, not a build step. Asset regeneration is a design change, so
 * it is run by hand and its output is committed; CI never runs it.
 *
 *   cd castadoo/assets && npm ci && npm run build
 *
 * ---------------------------------------------------------------------------
 * What is in source/
 * ---------------------------------------------------------------------------
 *   mark.svg      the CASTASOFT mark: 89.94 x 110.97, #303188 + #FAA61A
 *   wordmark.svg  the full CASTADOO lockup: 683.22 x 107.6
 *
 * A trap worth recording, because it changes the whole pipeline: the lockup is
 * NOT "mark + separate wordmark". The mark's two paths ARE the initial C, and
 * the four live <text> nodes supply "AST", "DO" and the O, giving C-A-S-T-A-D-O-O
 * read as CAST + ADOO. Dropping the mark would render "ASTADOO"; dropping the
 * text would leave a bare C. So the wordmark file is the complete artwork and
 * there is nothing to compose. Earlier drafts of this design described a
 * separate mark to be joined to a separate wordmark; measurement contradicts
 * that, and this file follows the measurement.
 *
 * ---------------------------------------------------------------------------
 * The one transformation: outline the live text
 * ---------------------------------------------------------------------------
 * Four <text>/<tspan> nodes draw at font-size 117.333px and 164px in Garamond.
 * Rasterising or shipping live text is wrong: a browser without Garamond
 * substitutes a different face, so the wordmark would render differently on the
 * user's machine than on ours. The recipe therefore replaces each <text> node
 * with equivalent <path> geometry produced by opentype.js from a Garamond font
 * file, which is what "outlined" means.
 *
 * Glyph advance widths are read from the font at run time; nothing about the
 * font's metrics is hard-coded. If the font file is absent the recipe stops
 * with an error rather than silently substituting a different typeface, because
 * a substituted face is indistinguishable from success at 62x20.
 *
 * ---------------------------------------------------------------------------
 * Output paths are upstream's, and filenames never change
 * ---------------------------------------------------------------------------
 * Keeping the filenames is what makes three code edits (webmanifest.py,
 * webclient_templates.xml) unnecessary. Sizes are preserved too, because they
 * are load-bearing: the portal footer draws logo.png at height="15", the brand
 * badge draws odoo_logo_tiny.png at width="62" height="20", and the customer
 * display sizes logo_inverse_white_206px.png by background-size: contain.
 * Changing a pixel dimension changes page layout, so dimensions are read from
 * the file being replaced and asserted, not chosen.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import opentype from "opentype.js";
import sharp from "sharp";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "..", "..");
const SOURCE = join(HERE, "source");

const NAVY = "#303188";
const ORANGE = "#FAA61A";

/** Font candidates, most specific first. The artwork names Garamond. */
const GARAMOND_CANDIDATES = [
  "C:/Windows/Fonts/GARA.TTF",
  "C:/Windows/Fonts/GARAIT.TTF",
  "/usr/share/fonts/truetype/msttcorefonts/GARA.TTF",
  "/Library/Fonts/Garamond.ttf",
];

function die(msg) {
  console.error(`\nERROR: ${msg}`);
  process.exit(1);
}

function loadGaramond() {
  for (const p of GARAMOND_CANDIDATES) {
    if (!existsSync(p)) continue;
    const font = opentype.loadSync(p);
    const family = font.names.fontFamily?.en ?? "?";
    if (!/garamond/i.test(family)) continue;
    console.log(`font: ${p} (family "${family}", upem ${font.unitsPerEm})`);
    return font;
  }
  die(
    "no Garamond font file found. The wordmark is authored in Garamond and the\n" +
      "outline must be produced from the same face, or the artwork changes. Install\n" +
      "Garamond, or add its path to GARAMOND_CANDIDATES.",
  );
}

/* -------------------------------------------------------------------------- */
/* SVG helpers                                                                */
/* -------------------------------------------------------------------------- */

/** Parse the four text runs out of the source wordmark. */
function readTextRuns(svg) {
  const runs = [];
  const re = /<text\b([^>]*)>([\s\S]*?)<\/text>/g;
  let m;
  while ((m = re.exec(svg)) !== null) {
    const attrs = m[1];
    const inner = m[2];
    const tspan = /<tspan\b([^>]*)>([\s\S]*?)<\/tspan>/.exec(inner);
    if (!tspan) continue;
    const content = decodeEntities(tspan[2]).trim();
    if (!content) continue; // text1 in the source is an empty stray node

    const styleAttr = /style="([^"]*)"/.exec(attrs)?.[1] ?? "";
    const tspStyle = /style="([^"]*)"/.exec(tspan[1])?.[1] ?? styleAttr;
    runs.push({
      content,
      fontSize: numFromStyle(styleAttr, "font-size"),
      x: Number(/x="([-\d.]+)"/.exec(tspan[1])?.[1]),
      y: Number(/y="([-\d.]+)"/.exec(tspan[1])?.[1]),
      fill: cssColor(tspStyle) ?? cssColor(styleAttr) ?? NAVY,
    });
  }
  return runs;
}

function numFromStyle(style, prop) {
  const m = new RegExp(`${prop}\\s*:\\s*([\\d.]+)`).exec(style);
  if (!m) die(`no ${prop} in style "${style}"`);
  return Number(m[1]);
}

/** First #rrggbb / #rgb in a style string. */
function cssColor(style) {
  const m = /fill\s*:\s*(#[0-9A-Fa-f]{3,6})/.exec(style ?? "");
  return m ? m[1] : null;
}

function decodeEntities(s) {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'");
}

function escapeXml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Convert one text run to path data at the run's own origin.
 *
 * opentype.js returns a path in y-down coordinates already, matching SVG, when
 * given `{y: baseline}`. The run's x/y are the tspan's, and each glyph is placed
 * by accumulating advance width, which is what the text layout did. Kerning is
 * left off deliberately: the source SVG sets no letter-spacing and the artwork
 * was not kerned, so adding it would change the lockup.
 */
function runToPath(font, run) {
  const path = font.getPath(run.content, run.x, run.y, run.fontSize);
  return path.toPathData(4);
}

/* -------------------------------------------------------------------------- */
/* Step 1: outline the wordmark                                               */
/* -------------------------------------------------------------------------- */

function buildWordmarkSvg(font) {
  const raw = readFileSync(join(SOURCE, "wordmark.svg"), "utf8");
  const runs = readTextRuns(raw);
  if (runs.length !== 3) {
    // 0.9.0 measurement: four <text> elements, one of which is empty (text1 has
    // no content and sits at y=223, outside the lockup). Requires exactly three
    // non-empty runs: AST, DO, O. A different count means the source changed.
    die(`expected 3 non-empty text runs in wordmark.svg, found ${runs.length}`);
  }
  for (const r of runs) {
    console.log(
      `  run "${r.content}" size ${r.fontSize} at (${r.x}, ${r.y}) fill ${r.fill}`,
    );
  }

  // Replace each <text>...</text> with a <path>. Done by walking the runs in
  // document order so the replacement cannot land on the wrong node.
  let out = raw;
  let cursor = 0;
  for (const run of runs) {
    const start = out.indexOf("<text", cursor);
    const end = out.indexOf("</text>", start) + "</text>".length;
    if (start === -1) die("text node vanished during replacement");
    const d = runToPath(font, run);
    const replacement =
      `<path d="${d}" fill="${run.fill}" ` +
      `id="outlined-${run.content.toLowerCase()}"/>`;
    out = out.slice(0, start) + replacement + out.slice(end);
    cursor = start + replacement.length;
  }

  // The stray empty <text id="text1"> is outside the lockup and now carries no
  // meaning; leaving it would ship an invisible dangling node.
  out = out.replace(/\s*<text\b[^>]*id="text1"[\s\S]*?<\/text>/g, "");

  // Strip editor metadata: it is not part of the artwork, it embeds a machine's
  // Inkscape version, and it is what makes the file churn on every re-save.
  out = out.replace(/\s*(?:inkscape|sodipodi):[a-zA-Z-]+="[^"]*"/g, "");
  out = out.replace(/\s*<sodipodi:namedview[\s\S]*?<\/sodipodi:namedview>/g, "");
  out = out.replace(/\s*<defs\b[^>]*>\s*<\/defs>/g, "");
  out = out.replace(/<!--[\s\S]*?-->\s*/g, "");
  out = out.replace(/\n{3,}/g, "\n\n");

  // A live <text> node would defeat the entire exercise.
  if (/<text\b/.test(out)) die("outlined wordmark still contains a <text> node");

  return out;
}

/** Plain standalone SVG of the mark, for the icon and the vector icon. */
function buildMarkSvg() {
  const raw = readFileSync(join(SOURCE, "mark.svg"), "utf8");
  // Keep the two paths and the viewBox; drop editor metadata.
  let out = raw
    .replace(/\s*(?:inkscape|sodipodi):[a-zA-Z-]+="[^"]*"/g, "")
    .replace(/\s*<sodipodi:namedview[\s\S]*?<\/sodipodi:namedview>/g, "")
    .replace(/\s*<defs\b[^>]*>\s*<\/defs>/g, "")
    .replace(/<!--[\s\S]*?-->\s*/g, "")
    .replace(/\n{3,}/g, "\n\n");

  // The source viewBox is NOT tight around the artwork: it is 89.94 x 110.97
  // while the ink occupies only the top 89.94 x 79.0, leaving 29% of the box
  // empty below the mark. Left in, that empty band is centred along with the
  // artwork, so every icon generated from this file sits visibly high. Measured
  // with sharp + an alpha bbox at density 1200; the numbers are in the comment
  // rather than recomputed at run time because a silent change of viewBox would
  // be a silent change of the lockup proportions.
  const TIGHT = "0 0 89.9405 78.9986";
  if (/viewBox="[^"]*"/.test(out)) {
    out = out.replace(/viewBox="[^"]*"/, `viewBox="${TIGHT}"`);
  } else {
    out = out.replace(/<svg\b/, `<svg viewBox="${TIGHT}"`);
  }
  // width/height must follow the viewBox or a renderer that honours them will
  // letterbox the trimmed artwork back into the old, taller canvas.
  out = out.replace(/\swidth="[^"]*"/, ` width="89.9405"`);
  out = out.replace(/\sheight="[^"]*"/, ` height="78.9986"`);

  // Ensure root has xmlns (the source declares it, but after attribute
  // stripping the declaration can be the thing removed). Guard, do not assume.
  if (!/xmlns="http:\/\/www\.w3\.org\/2000\/svg"/.test(out)) {
    out = out.replace(/<svg\b/, '<svg xmlns="http://www.w3.org/2000/svg"');
  }
  return out;
}

/**
 * Square icon from the mark, on a solid or transparent ground.
 *
 * The mark is 0.81:1 (portrait). On a square canvas it is centered with a
 * margin, never stretched: a stretched mark is a different logo. `maskable`
 * follows the PWA rule that the safe zone is the central 80%, so the mark is
 * drawn at 62% of the canvas - inside 80% with room for the rounded-corner crop
 * Android and iOS apply.
 */
async function squareIcon(markPng, size, opts = {}) {
  const { background, markRatio = 0.62 } = opts;
  const inner = Math.round(size * markRatio);
  // Fit inside a SQUARE of `inner`, not by height: the mark is 1.14:1 (wider than
  // tall) so a height-only fit would make it wider than the box it was sized for.
  const resized = await sharp(markPng)
    .resize({ width: inner, height: inner, fit: "inside" })
    .toBuffer();
  return sharp({
    create: {
      width: size,
      height: size,
      channels: 4,
      background: background ?? { r: 0, g: 0, b: 0, alpha: 0 },
    },
  })
    .composite([{ input: resized, gravity: "center" }])
    .png()
    .toBuffer();
}

/** Multi-size .ico. sharp cannot write ICO, so the container is written here. */
function buildIco(pngBuffers) {
  const count = pngBuffers.length;
  const HEADER = 6;
  const ENTRY = 16;
  let offset = HEADER + ENTRY * count;
  const dir = Buffer.alloc(HEADER + ENTRY * count);
  dir.writeUInt16LE(0, 0); // reserved
  dir.writeUInt16LE(1, 2); // type: icon
  dir.writeUInt16LE(count, 4);

  pngBuffers.forEach((buf, i) => {
    const { width, height } = pngSize(buf);
    const at = HEADER + ENTRY * i;
    dir.writeUInt8(width >= 256 ? 0 : width, at + 0);
    dir.writeUInt8(height >= 256 ? 0 : height, at + 1);
    dir.writeUInt8(0, at + 2); // palette count
    dir.writeUInt8(0, at + 3); // reserved
    dir.writeUInt16LE(1, at + 4); // colour planes
    dir.writeUInt16LE(32, at + 6); // bits per pixel
    dir.writeUInt32LE(buf.length, at + 8);
    dir.writeUInt32LE(offset, at + 12);
    offset += buf.length;
  });

  return Buffer.concat([dir, ...pngBuffers]);
}

/** Read width/height from a PNG's IHDR, avoiding a second decode. */
function pngSize(buf) {
  if (buf.readUInt32BE(0) !== 0x89504e47) die("not a PNG");
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

/* -------------------------------------------------------------------------- */
/* Step 2: the outputs                                                        */
/* -------------------------------------------------------------------------- */

async function main() {
  const font = loadGaramond();

  console.log("\n[1/4] outlining the wordmark");
  const wordmarkSvg = buildWordmarkSvg(font);
  const markSvg = buildMarkSvg();

  const wordmarkPng = await sharp(Buffer.from(wordmarkSvg)).png().toBuffer();
  // Render the mark at high resolution once; every icon downsamples from it, so
  // the small sizes are properly antialiased instead of aliased from 96px.
  const markPng = await sharp(Buffer.from(markSvg), { density: 1200 })
    .png()
    .toBuffer();

  const wm = await sharp(wordmarkPng).metadata();
  console.log(`  outlined wordmark raster: ${wm.width}x${wm.height}`);

  console.log("\n[2/4] wordmark and lockup blobs");

  // --- logo.png: drawn at height="15" in the portal footer and at h-75 in the
  // POS navbar, so the canvas is tight to the lockup and width 180 is kept.
  await write("addons/web/static/img/logo.png", await tight(wordmarkPng, 180));

  // --- logo2.png: database manager and the POS customer-display page. Both
  // size it by width, so the width is kept.
  await write("addons/web/static/img/logo2.png", await tight(wordmarkPng, 300));

  // --- odoo_logo_tiny.png: the "Powered by" badge, drawn with height: 1em and
  // width: auto, i.e. sized by HEIGHT. It is therefore the mark, not the
  // wordmark - an eight-letter serif lockup at 1em is illegible, while the mark
  // reads. The 62x20 the markup also names is overridden by that inline style,
  // so a tight 20px-tall canvas is what actually gets laid out.
  await write("addons/web/static/img/odoo_logo_tiny.png", await markAtHeight(markPng, 20));

  // --- logo_inverse_white_206px.png: white on transparent, used as a CSS
  // background with background-size: contain on the POS customer display's dark
  // panel. Must be white, and must not be flattened onto a background - the
  // transparency is what lets the dark panel show through.
  await write(
    "addons/web/static/img/logo_inverse_white_206px.png",
    await tight(wordmarkPng, 627, { recolor: "#FFFFFF" }),
  );

  console.log("\n[3/4] icons");

  // --- favicon.ico: upstream is a single 16x16 frame. 16 alone is what the
  // tab bar uses, but a 32px frame costs nothing and halves the blur on HiDPI.
  // The extra frame is additive: it cannot break a consumer that asks for 16.
  const favSizes = [16, 32, 48];
  const favFrames = [];
  for (const s of favSizes) {
    favFrames.push(await squareIcon(markPng, s, { markRatio: 0.88 }));
  }
  await write("addons/web/static/img/favicon.ico", buildIco(favFrames));

  // The POS and installer favicons are byte-identical to the web one upstream
  // (measured: all three are 1150 B, 16x16). Same treatment, one blob reused.
  await write("addons/point_of_sale/static/src/img/favicon.ico", buildIco(favFrames));
  await write("setup/win32/static/pixmaps/odoo-icon.ico", buildIco(favFrames));

  // --- PWA icons: 192 and 512, transparent, maskable-safe margin.
  await write(
    "addons/web/static/img/odoo-icon-192x192.png",
    await squareIcon(markPng, 192, {}),
  );
  await write(
    "addons/web/static/img/odoo-icon-512x512.png",
    await squareIcon(markPng, 512, {}),
  );

  // --- iOS: upstream is 500x500 OPAQUE RGB. iOS composites a transparent
  // apple-touch-icon onto black, so the ground must be filled. White is used
  // because the mark is navy+orange and reads on white; the file was opaque
  // white upstream too. 500x500 is preserved - a size change here is a size
  // change on every iOS home screen that already installed the app.
  await write(
    "addons/web/static/img/odoo-icon-ios.png",
    await squareIcon(markPng, 500, {
      background: { r: 255, g: 255, b: 255, alpha: 1 },
      markRatio: 0.7,
    }),
  );

  // --- odoo-icon.svg: vector mark, same viewBox as upstream's slot.
  await write("addons/web/static/img/odoo-icon.svg", Buffer.from(markSvg));

  // --- website_links fallback: 16x16, square, transparent.
  await write(
    "addons/website_links/static/img/default_favicon.png",
    await squareIcon(markPng, 16, { markRatio: 0.9 }),
  );

  console.log("\n[4/4] installer bitmaps");

  // --- odoo-intro.bmp: 164x314 24-bit, the NSIS welcome page bitmap. Both
  // dimensions are fixed by the MUI welcome page - NSIS does not scale it - so
  // unlike every other target the canvas cannot be made tight. The lockup is
  // placed centred and its aspect preserved. BMP carries no alpha, so the
  // background is painted in: 24-bit BI_RGB throughout.
  await writeBmp(
    "setup/win32/static/pixmaps/odoo-intro.bmp",
    await placeOn(wordmarkPng, 164, 314, { inset: 8 }),
  );

  // --- odoo-slogan.bmp: 500x71, header image. Upstream prints the odoo.com URL
  // beside the logo; that URL is a user-visible string and the CASTASOFT
  // address replaces it.
  await writeBmp(
    "setup/win32/static/pixmaps/odoo-slogan.bmp",
    await slogan(markPng, wordmarkPng, 500, 71),
  );

  const darkSvg = await recolorSvg(wordmarkSvg, "#FFFFFF");
  await write("addons/web/static/img/odoo_logo.svg", Buffer.from(wordmarkSvg));
  await write("addons/web/static/img/odoo_logo_dark.svg", Buffer.from(darkSvg));

  console.log("\nall outputs written");
}

/* -------------------------------------------------------------------------- */
/* Composition primitives                                                     */
/* -------------------------------------------------------------------------- */

/**
 * Resize artwork to a target width and return a canvas TIGHT around it.
 *
 * Why tight and not the upstream canvas: CASTADOO's lockup is 6.35:1 where
 * Odoo's "odoo" wordmark was 2.28:1. Letterboxing our wide artwork into the old
 * taller canvas puts the ink in a vertical band with empty space above and
 * below, and the two consumers that matter size by HEIGHT - the portal footer
 * draws logo.png at height="15", the POS navbar at h-75. Against a 79px-tall
 * canvas that renders the wordmark about 5px tall: present, and unreadable.
 * A canvas whose aspect matches the artwork makes height-size the ink-size.
 *
 * Width is what is preserved, because the assets are positioned by their left
 * edge (left: 0 in the installer slogan, mx-auto in the database manager).
 */
async function tight(buf, width, opts = {}) {
  const { recolor, background } = opts;
  let src = buf;
  if (recolor) src = await recolorTo(src, recolor);
  const resized = await sharp(src).resize({ width }).toBuffer();
  if (!background) return resized; // keep transparency
  const meta = await sharp(resized).metadata();
  return sharp(resized).flatten({ background }).png().toBuffer();
}

/** Resize artwork to a target height, transparent canvas tight around it. */
async function markAtHeight(buf, height) {
  return sharp(buf).resize({ height }).png().toBuffer();
}

/**
 * Fit artwork inside a FIXED canvas, centred, aspect preserved.
 *
 * Only for the installer bitmaps: NSIS sizes the welcome page to the bitmap it
 * is given, so 164x314 and 500x71 are not free choices and the canvas cannot be
 * made tight.
 */
async function placeOn(buf, w, h, opts = {}) {
  const { background = "#ffffff", inset = 0 } = opts;
  const inner = await sharp(buf)
    .resize({ width: w - inset * 2, height: h - inset * 2, fit: "inside" })
    .toBuffer();
  const meta = await sharp(inner).metadata();
  const plate = await sharp({
    create: { width: w, height: h, channels: 3, background },
  })
    .png()
    .toBuffer();
  return sharp(plate)
    .composite([
      {
        input: inner,
        left: Math.round((w - meta.width) / 2),
        top: Math.round((h - meta.height) / 2),
      },
    ])
    .png()
    .toBuffer();
}

/** Bare fixed-size plate, for composing several layers by hand. */
async function plate(w, h, background = "#ffffff") {
  return sharp({ create: { width: w, height: h, channels: 3, background } })
    .png()
    .toBuffer();
}

/** The mark in a wide thin badge, sized by HEIGHT and centred, never stretched. */
async function badge(markPng, w, h, { fill = 0.86 } = {}) {
  const inner = await sharp(markPng)
    .resize({ height: Math.round(h * fill), fit: "inside" })
    .toBuffer();
  const meta = await sharp(inner).metadata();
  return sharp(await plate(w, h, "#ffffff"))
    .composite([
      {
        input: inner,
        left: Math.round((w - meta.width) / 2),
        top: Math.round((h - meta.height) / 2),
      },
    ])
    .png()
    .toBuffer();
}

/**
 * The NSIS header image: mark + wordmark on the left, the CASTASOFT address on
 * the right, replacing upstream's odoo.com URL.
 *
 * Text is rasterised from Arial with librsvg via an SVG wrapper. Arial is chosen
 * because it ships with every Windows install and the header image is 71px tall,
 * where a serif at this size turns to mush - the wordmark keeps the serif, the
 * address line does not.
 */
async function slogan(markPng, wordmarkPng, w, h) {
  const LOCKUP_H = Math.round(h * 0.62);
  const lockup = await sharp(wordmarkPng)
    .resize({ height: LOCKUP_H, fit: "inside" })
    .toBuffer();
  const lm = await sharp(lockup).metadata();

  const label = "castasoft.yukreasi.id";
  const GAP = 16;
  const PAD_R = 12;
  const left = 10;
  const available = w - PAD_R - (left + lm.width) - GAP;

  // Size the label from measured advance width, not from a guess: the first
  // attempt hard-coded 26px and the label ran back over the lockup, because
  // "castasoft.yukreasi.id" at 26px Arial is ~280px wide and only ~200px is
  // left once the lockup is placed. Fitting to `available` makes the overlap
  // impossible rather than merely unlikely.
  const arial = loadFontSafe(["C:/Windows/Fonts/arial.ttf", "/Library/Fonts/Arial.ttf",
                              "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"]);
  let fontSize = 12;
  if (arial) {
    fontSize = 24;
    while (fontSize > 7 && arial.getAdvanceWidth(label, fontSize) > available) {
      fontSize -= 1;
    }
    const fitted = arial.getAdvanceWidth(label, fontSize);
    console.log(
      `  slogan: lockup ${lm.width}x${lm.height}, label ${fitted.toFixed(0)}px ` +
        `at ${fontSize}px in ${available}px available`,
    );
    if (fitted > available) {
      die(`slogan label does not fit: ${fitted.toFixed(0)}px > ${available}px`);
    }
  } else {
    console.log("  slogan: no Arial found, label rendered at the 12px floor");
  }

  const bg = await sharp(await plate(w, h, "#ffffff")).png().toBuffer();

  const textPng = await sharp(
    Buffer.from(
      `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">` +
        `<text x="${w - PAD_R}" y="${Math.round(h / 2)}" ` +
        `font-family="Arial, Helvetica, sans-serif" font-size="${fontSize}" ` +
        `fill="#666666" text-anchor="end" dominant-baseline="central">` +
        `${escapeXml(label)}</text></svg>`,
    ),
  )
    .png()
    .toBuffer();

  return sharp(bg)
    .composite([
      { input: lockup, left, top: Math.round((h - lm.height) / 2) },
      { input: textPng, left: 0, top: 0 },
    ])
    .png()
    .toBuffer();
}

/** Load the first font that exists, or null. Used only for the installer label. */
function loadFontSafe(candidates) {
  for (const p of candidates) {
    if (!existsSync(p)) continue;
    try {
      return opentype.loadSync(p);
    } catch {
      continue;
    }
  }
  return null;
}

/** Replace every solid fill in an SVG with one colour, keeping alpha. */
async function recolorSvg(svg, colour) {
  return svg
    .replace(/#[0-9A-Fa-f]{6}/g, colour)
    .replace(/fill="#[0-9A-Fa-f]{6}"/g, `fill="${colour}"`);
}

/** Recolour a raster: keep the alpha channel, flatten every pixel to `colour`. */
async function recolorTo(buf, colour) {
  const { data, info } = await sharp(buf)
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const r = parseInt(colour.slice(1, 3), 16);
  const g = parseInt(colour.slice(3, 5), 16);
  const b = parseInt(colour.slice(5, 7), 16);
  for (let i = 0; i < data.length; i += 4) {
    data[i] = r;
    data[i + 1] = g;
    data[i + 2] = b;
  }
  return sharp(data, { raw: { width: info.width, height: info.height, channels: 4 } })
    .png()
    .toBuffer();
}

/* -------------------------------------------------------------------------- */
/* Sinks                                                                      */
/* -------------------------------------------------------------------------- */

const written = [];

async function write(rel, buf) {
  const path = join(REPO, rel);
  if (!existsSync(path)) {
    die(`${rel} does not exist upstream; filenames must never change`);
  }
  const before = readFileSync(path);
  // Every helper above returns a Buffer, but awaiting is harmless and keeps a
  // future async helper from silently writing a Promise to disk.
  const after = Buffer.isBuffer(buf) ? buf : await buf;
  writeFileSync(path, after);
  written.push({ rel, from: before.length, to: after.length });
}

/** sharp cannot emit BMP. Convert the PNG through an explicit 24-bit BMP write. */
async function writeBmp(rel, buf) {
  const { data, info } = await sharp(buf)
    .flatten({ background: "#ffffff" })
    .raw()
    .toBuffer({ resolveWithObject: true });
  if (info.channels !== 3) die(`expected 3 channels for BMP, got ${info.channels}`);

  const w = info.width;
  const h = info.height;
  const rowSize = Math.floor((24 * w + 31) / 32) * 4;
  const pixelBytes = rowSize * h;
  const header = Buffer.alloc(54);
  const fileSize = 54 + pixelBytes;

  header.write("BM", 0, "ascii");
  header.writeUInt32LE(fileSize, 2);
  header.writeUInt32LE(0, 6);
  header.writeUInt32LE(54, 10);
  header.writeUInt32LE(40, 14); // BITMAPINFOHEADER
  header.writeInt32LE(w, 18);
  header.writeInt32LE(h, 22); // positive: bottom-up
  header.writeUInt16LE(1, 26); // planes
  header.writeUInt16LE(24, 28); // bpp
  header.writeUInt32LE(0, 30); // BI_RGB
  header.writeUInt32LE(pixelBytes, 34);
  header.writeInt32LE(2835, 38);
  header.writeInt32LE(2835, 42);
  header.writeUInt32LE(0, 46);
  header.writeUInt32LE(0, 50);

  const px = Buffer.alloc(pixelBytes);
  for (let y = 0; y < h; y++) {
    // BMP rows are stored bottom-up and channels are BGR.
    const srcRow = (h - 1 - y) * w * 3;
    const dstRow = y * rowSize;
    for (let x = 0; x < w; x++) {
      px[dstRow + x * 3 + 0] = data[srcRow + x * 3 + 2];
      px[dstRow + x * 3 + 1] = data[srcRow + x * 3 + 1];
      px[dstRow + x * 3 + 2] = data[srcRow + x * 3 + 0];
    }
  }

  const path = join(REPO, rel);
  if (!existsSync(path)) die(`${rel} does not exist upstream`);
  const before = readFileSync(path).length;
  writeFileSync(path, Buffer.concat([header, px]));
  written.push({ rel, from: before, to: 54 + pixelBytes });
}

main()
  .then(() => {
    console.log("\n" + "-".repeat(76));
    console.log("path".padEnd(56) + "before".padStart(9) + "after".padStart(10));
    console.log("-".repeat(76));
    for (const w of written) {
      console.log(w.rel.padEnd(56) + String(w.from).padStart(9) + String(w.to).padStart(10));
    }
    console.log("-".repeat(76));
    console.log(`${written.length} files rewritten in place`);
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
