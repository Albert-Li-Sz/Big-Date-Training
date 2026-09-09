/** 保存课程报告所需的本地系统实测截图。 */

import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const playwrightPath =
  "/Users/albert_li/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
const { chromium } = await import(pathToFileURL(playwrightPath).href);

const outputDir = path.resolve(
  process.argv[2] ?? new URL("../docs/screenshots", import.meta.url).pathname,
);
const mode = process.argv[3] ?? "all";
if (!["all", "app", "services"].includes(mode)) {
  throw new Error("mode 必须是 all、app 或 services");
}
await fs.mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
  args: ["--disable-dev-shm-usage"],
});

async function openPage(viewport) {
  const context = await browser.newContext({ viewport, locale: "zh-CN" });
  const page = await context.newPage();
  return { context, page };
}

async function captureStreamlit() {
  const desktop = await openPage({ width: 1440, height: 1000 });
  await desktop.page.goto("http://127.0.0.1:8888", { waitUntil: "domcontentloaded" });
  await desktop.page.getByText("TOP 1 推荐岗位", { exact: true }).waitFor({ timeout: 30000 });
  await desktop.page.screenshot({
    path: path.join(outputDir, "streamlit-student-desktop.png"),
    fullPage: false,
  });
  await desktop.page.getByText("岗位找人才", { exact: true }).click();
  await desktop.page.getByText("TOP 1 推荐候选人", { exact: true }).waitFor({ timeout: 30000 });
  await desktop.page.screenshot({
    path: path.join(outputDir, "streamlit-job-desktop.png"),
    fullPage: false,
  });
  await desktop.context.close();

  const mobile = await openPage({ width: 390, height: 844 });
  await mobile.page.goto("http://127.0.0.1:8888", { waitUntil: "domcontentloaded" });
  await mobile.page.getByText("TOP 1 推荐岗位", { exact: true }).waitFor({ timeout: 30000 });
  await mobile.page.screenshot({
    path: path.join(outputDir, "streamlit-student-mobile.png"),
    fullPage: false,
  });
  await mobile.context.close();
}

async function captureService(url, outputName, readyText) {
  const session = await openPage({ width: 1440, height: 900 });
  await session.page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
  if (readyText) {
    await session.page
      .getByText(readyText, { exact: false })
      .first()
      .waitFor({ timeout: 5000 })
      .catch(() => undefined);
  }
  await session.page.waitForTimeout(1500);
  await session.page.screenshot({
    path: path.join(outputDir, outputName),
    fullPage: false,
  });
  await session.context.close();
}

try {
  if (mode === "all" || mode === "app") {
    await captureStreamlit();
  }
  if (mode === "all" || mode === "services") {
    await captureService(
      "http://127.0.0.1:9870/explorer.html#/resume_matching",
      "hdfs-resume-matching.png",
      "resume_matching",
    );
    await captureService(
      "http://127.0.0.1:8088/cluster/nodes",
      "yarn-nodes.png",
      "Nodes of the cluster",
    );
    await captureService(
      "http://127.0.0.1:4040/jobs/",
      "spark-jobs.png",
      "Spark Jobs",
    );
  }
} finally {
  await browser.close();
}

console.log(`Screenshots saved to ${outputDir}`);
