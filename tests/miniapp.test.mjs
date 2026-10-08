// Tests the Mini App's pure text functions by extracting them from index.html.
// Run: node tests/miniapp.test.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";

const html = readFileSync(new URL("../miniapp/index.html", import.meta.url), "utf8").replace(/\r\n/g, "\n");
const grab = name => {
  const m = html.match(new RegExp(`function ${name}\\b[\\s\\S]*?\\n}\\n`));
  assert.ok(m, `function ${name} not found in miniapp/index.html`);
  return m[0];
};
const { normalize, sentences } = new Function(`${grab("normalize")}\n${grab("sentences")}\nreturn { normalize, sentences };`)();

// same golden cases as tests/test_textproc.py
assert.equal(normalize("at 7:30, then 12:00, 6:05"), "at 7 30, then 12 o'clock, 6 oh 5");
assert.equal(normalize("ratio 3:1:2 and 1:23:45 and Note: done"), "ratio 3:1:2 and 1:23:45 and Note: done");
assert.equal(normalize("Dr. Smith lives on Elm St. near the park."), "Dr. Smith lives on Elm Street near the park.");
assert.equal(normalize("He moved to Baker St."), "He moved to Baker Street.");
assert.equal(normalize("Turn left on Main St., then right."), "Turn left on Main Street, then right.");
assert.equal(normalize("She visited St. Louis last year."), "She visited Saint Louis last year.");
assert.equal(normalize("It was the 1st St. of the list"), "It was the 1st St. of the list");
assert.deepEqual(
  sentences("Line one. Two.\nLine three\n\nPara two. End"),
  [{ text: "Line one. Two.", pause: 1 }, { text: "Line three", pause: 2 }, { text: "Para two. End", pause: 0 }],
);
assert.deepEqual(sentences(""), []);
console.log("miniapp tests passed");
