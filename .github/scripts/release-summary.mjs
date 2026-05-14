import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const skillsIndexPath = path.join(repoRoot, "skills", "index.json");
const outDir = path.join(repoRoot, ".github", "out");
const outFile = path.join(outDir, "release-summary.json");

const skillsIndex = JSON.parse(fs.readFileSync(skillsIndexPath, "utf8"));

const summary = {
  generatedAt: new Date().toISOString(),
  skillCount: skillsIndex.skills.length,
  skills: skillsIndex.skills
};

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(outFile, `${JSON.stringify(summary, null, 2)}\n`, "utf8");

console.log(`Wrote ${path.relative(repoRoot, outFile)}`);
