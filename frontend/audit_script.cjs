const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function delay(time) {
  return new Promise(function(resolve) { 
      setTimeout(resolve, time)
  });
}

async function runAudit() {
  console.log("Starting Puppeteer Audit...");
  const browser = await puppeteer.launch({ 
    headless: "new", 
    defaultViewport: { width: 1440, height: 900 },
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
  });
  const page = await browser.newPage();
  
  const artifactDir = path.join(__dirname, "audit-artifacts");
  if (!fs.existsSync(artifactDir)){
      fs.mkdirSync(artifactDir, { recursive: true });
  }

  try {
    // 1. Login Page
    console.log("Navigating to /login...");
    await page.goto('http://127.0.0.1:5173/login', { waitUntil: 'networkidle0' });
    await delay(2000);
    await page.screenshot({ path: path.join(artifactDir, 'audit_login.png') });
    console.log("Saved audit_login.png");

    // 2. Click login to go to dashboard
    console.log("Logging in...");
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Sign in'));
      if (btn) btn.click();
    });
    await delay(5000); // Wait for data to load
    await page.screenshot({ path: path.join(artifactDir, 'audit_dashboard.png') });
    console.log("Saved audit_dashboard.png");

    // 3. Queue Page
    console.log("Navigating to /queue...");
    await page.goto('http://127.0.0.1:5173/queue', { waitUntil: 'networkidle0' });
    await delay(3000);
    await page.screenshot({ path: path.join(artifactDir, 'audit_queue.png') });
    console.log("Saved audit_queue.png");

    // 4. Investigation Workspace
    console.log("Navigating to /investigation/C_1...");
    await page.goto('http://127.0.0.1:5173/investigation/C_1', { waitUntil: 'networkidle0' });
    await delay(5000);
    await page.screenshot({ path: path.join(artifactDir, 'audit_workspace.png') });
    console.log("Saved audit_workspace.png");

    // 5. Playground
    console.log("Navigating to /playground...");
    await page.goto('http://127.0.0.1:5173/playground', { waitUntil: 'networkidle0' });
    await delay(3000);
    
    // Type in playground
    await page.type('textarea[placeholder*="Ask FinShield"]', 'Analyze dataset for suspicious patterns');
    await page.click('button:has(svg.lucide-send)');
    console.log("Waiting for playground response...");
    await delay(15000); // wait for investigation to run
    await page.screenshot({ path: path.join(artifactDir, 'audit_playground.png') });
    console.log("Saved audit_playground.png");

  } catch (error) {
    console.error("Audit failed:", error);
  } finally {
    await browser.close();
    console.log("Puppeteer closed.");
  }
}

runAudit();
