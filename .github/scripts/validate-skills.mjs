import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const skillsRoot = path.join(repoRoot, "skills");
const skillsIndexPath = path.join(skillsRoot, "index.json");
const absolutePatterns = [/\/Users\//, /\/home\//, /\/private\//, /[A-Za-z]:\\/];
const errors = [];

function readFile(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function hasAbsolutePath(text) {
  return absolutePatterns.some((pattern) => pattern.test(text));
}

function parseFrontmatter(filePath) {
  const lines = readFile(filePath).split(/\r?\n/);
  if (lines[0] !== "---") {
    return {};
  }
  const meta = {};
  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (line === "---") {
      break;
    }
    const idx = line.indexOf(":");
    if (idx === -1) {
      continue;
    }
    const key = line.slice(0, idx).trim();
    const value = line.slice(idx + 1).trim().replace(/^["']|["']$/g, "");
    meta[key] = value;
  }
  return meta;
}

function validateMarkdownLinks(filePath) {
  const content = readFile(filePath);
  const linkPattern = /\[[^\]]+\]\(([^)]+)\)/g;
  let match;
  while ((match = linkPattern.exec(content)) !== null) {
    const target = match[1];
    if (
      target.startsWith("http://") ||
      target.startsWith("https://") ||
      target.startsWith("mailto:") ||
      target.startsWith("#")
    ) {
      continue;
    }
    const cleanTarget = target.split("#")[0];
    if (!cleanTarget) {
      continue;
    }
    const resolved = path.resolve(path.dirname(filePath), cleanTarget);
    if (!fs.existsSync(resolved)) {
      errors.push(`Broken local markdown link: ${path.relative(repoRoot, filePath)} -> ${target}`);
    }
  }
}

const categories = ["business", "dev"];
const seen = new Set();
const actualSkills = [];

for (const category of categories) {
  const categoryDir = path.join(skillsRoot, category);
  if (!fs.existsSync(categoryDir)) {
    continue;
  }
  for (const entry of fs.readdirSync(categoryDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) {
      continue;
    }
    if (seen.has(entry.name)) {
      errors.push(`Duplicate skill slug across categories: ${entry.name}`);
      continue;
    }
    seen.add(entry.name);

    const skillDir = path.join(categoryDir, entry.name);
    const skillMd = path.join(skillDir, "SKILL.md");
    if (!fs.existsSync(skillMd)) {
      errors.push(`Missing SKILL.md: ${path.relative(repoRoot, skillDir)}`);
      continue;
    }

    const meta = parseFrontmatter(skillMd);
    if (!meta.name) {
      errors.push(`Missing 'name' in ${path.relative(repoRoot, skillMd)}`);
    }
    if (!meta.description) {
      errors.push(`Missing 'description' in ${path.relative(repoRoot, skillMd)}`);
    }

    const skillContent = readFile(skillMd);
    if (hasAbsolutePath(skillContent)) {
      errors.push(`Absolute path detected in ${path.relative(repoRoot, skillMd)}`);
    }
    validateMarkdownLinks(skillMd);

    const referencesDir = path.join(skillDir, "references");
    if (fs.existsSync(referencesDir)) {
      for (const ref of fs.readdirSync(referencesDir)) {
        const refPath = path.join(referencesDir, ref);
        if (fs.statSync(refPath).isFile() && refPath.endsWith(".md")) {
          const refContent = readFile(refPath);
          if (hasAbsolutePath(refContent)) {
            errors.push(`Absolute path detected in ${path.relative(repoRoot, refPath)}`);
          }
          validateMarkdownLinks(refPath);
        }
      }
    }

    actualSkills.push({
      slug: entry.name,
      category,
      path: `skills/${category}/${entry.name}`,
      name: meta.name || "",
      description: meta.description || ""
    });
  }
}

for (const filePath of [
  path.join(repoRoot, "README.md"),
  path.join(repoRoot, "AGENTS.md"),
  path.join(repoRoot, ".env.example")
]) {
  if (!fs.existsSync(filePath)) {
    errors.push(`Missing required file: ${path.relative(repoRoot, filePath)}`);
    continue;
  }
  const content = readFile(filePath);
  if (hasAbsolutePath(content)) {
    errors.push(`Absolute path detected in ${path.relative(repoRoot, filePath)}`);
  }
  if (filePath.endsWith(".md")) {
    validateMarkdownLinks(filePath);
  }
}

const claudeManifest = path.join(repoRoot, ".claude-plugin", "manifest.json");
if (!fs.existsSync(claudeManifest)) {
  errors.push("Missing .claude-plugin/manifest.json");
}

if (!fs.existsSync(skillsIndexPath)) {
  errors.push("Missing skills/index.json");
} else {
  const declaredIndex = JSON.parse(readFile(skillsIndexPath));
  const declared = new Set((declaredIndex.skills || []).map((item) => `${item.category}/${item.slug}`));
  const actual = new Set(actualSkills.map((item) => `${item.category}/${item.slug}`));
  for (const item of actualSkills) {
    if (!declared.has(`${item.category}/${item.slug}`)) {
      errors.push(`skills/index.json missing ${item.category}/${item.slug}`);
    }
  }
  for (const item of declaredIndex.skills || []) {
    if (!actual.has(`${item.category}/${item.slug}`)) {
      errors.push(`skills/index.json contains unknown ${item.category}/${item.slug}`);
    }
  }
}

if (errors.length > 0) {
  for (const error of errors) {
    console.error(`ERROR: ${error}`);
  }
  process.exit(1);
}

console.log("Validation passed.");
