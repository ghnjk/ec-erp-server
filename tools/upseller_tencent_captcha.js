#!/usr/bin/env node
/**
 * 在 Node.js + jsdom 中调用腾讯云 TencentCaptcha(smart)，输出 ticket/randstr JSON。
 * 不依赖 Chrome / Selenium。
 *
 * Usage:
 *   node upseller_tencent_captcha.js [captchaAppId]
 */
const { JSDOM } = require("jsdom");
const https = require("https");
const http = require("http");

const AID = process.argv[2] || "191710692";
const PAGE_URL = process.env.UPSELLER_LOGIN_URL || "https://app.upseller.com/zh-CN/login";
const TIMEOUT_MS = Number(process.env.UPSELLER_TENCENT_TIMEOUT_MS || 60000);

function fetchText(url) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith("https") ? https : http;
    const req = lib.get(url, { headers: { "User-Agent": "Mozilla/5.0" } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        fetchText(res.headers.location).then(resolve, reject);
        return;
      }
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    });
    req.on("error", reject);
    req.setTimeout(30000, () => {
      req.destroy(new Error("download timeout"));
    });
  });
}

function installCanvasStub(window) {
  window.HTMLCanvasElement.prototype.getContext = function () {
    return {
      fillRect() {},
      clearRect() {},
      getImageData() {
        return { data: new Uint8ClampedArray(4) };
      },
      putImageData() {},
      createImageData() {
        return [];
      },
      setTransform() {},
      drawImage() {},
      save() {},
      fillText() {},
      restore() {},
      beginPath() {},
      moveTo() {},
      lineTo() {},
      closePath() {},
      stroke() {},
      translate() {},
      scale() {},
      rotate() {},
      arc() {},
      fill() {},
      measureText() {
        return { width: 0 };
      },
      transform() {},
      rect() {},
      clip() {},
      canvas: this,
    };
  };
  window.HTMLCanvasElement.prototype.toDataURL = () =>
    "data:image/png;base64,iVBORw0KGgo=";
}

async function main() {
  const html = "<!doctype html><html><head></head><body><div id='root'></div></body></html>";
  const dom = new JSDOM(html, {
    url: PAGE_URL,
    referrer: PAGE_URL,
    runScripts: "dangerously",
    resources: "usable",
    pretendToBeVisual: true,
    beforeParse: installCanvasStub,
  });
  const { window } = dom;
  global.window = window;
  global.document = window.document;
  global.navigator = window.navigator;
  global.self = window;

  const script = await fetchText("https://turing.captcha.qcloud.com/TJCaptcha.js");
  window.eval(script);
  if (typeof window.TencentCaptcha !== "function") {
    throw new Error("TencentCaptcha not loaded");
  }

  const result = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("TencentCaptcha timeout")), TIMEOUT_MS);
    try {
      const captcha = new window.TencentCaptcha(
        AID,
        (res) => {
          clearTimeout(timer);
          resolve(res);
        },
        { type: "smart" }
      );
      captcha.show();
    } catch (e) {
      clearTimeout(timer);
      reject(e);
    }
  });

  if (!result || result.ret !== 0 || !result.ticket) {
    throw new Error(`TencentCaptcha failed: ${JSON.stringify(result)}`);
  }
  process.stdout.write(
    JSON.stringify({
      ticket: result.ticket,
      randstr: result.randstr,
      sid: result.sid,
      verifyDuration: result.verifyDuration,
      actionDuration: result.actionDuration,
    })
  );
}

main().catch((e) => {
  process.stderr.write(String(e && e.stack ? e.stack : e) + "\n");
  process.exit(1);
});
