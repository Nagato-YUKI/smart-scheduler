const { chromium } = require('@playwright/test');

const BASE_URL = 'https://nagato-yuki.github.io/smart-scheduler/';

async function deepAnalysis() {
  console.log('========== 深度分析测试 ==========\n');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'zh-CN',
  });

  const page = await context.newPage();

  // 收集所有请求和响应
  const failedRequests = [];
  const successfulRequests = [];

  page.on('request', request => {
    // 记录所有请求
  });

  page.on('response', async response => {
    const status = response.status();
    const url = response.url();
    if (status >= 400) {
      failedRequests.push({ url, status });
    } else {
      successfulRequests.push({ url, status });
    }
  });

  // 访问首页
  console.log('--- 访问首页并分析资源加载 ---');
  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(5000);

  // 1. 打印所有失败的请求
  console.log(`\n失败的请求 (${failedRequests.length}个):`);
  failedRequests.forEach((req, i) => {
    console.log(`  ${i + 1}. [${req.status}] ${req.url}`);
  });

  // 2. 打印成功加载的资源
  console.log(`\n成功加载的资源 (${successfulRequests.length}个):`);
  successfulRequests.forEach((req, i) => {
    console.log(`  ${i + 1}. [${req.status}] ${req.url}`);
  });

  // 3. 检查页面DOM结构
  console.log('\n--- 页面DOM结构分析 ---');

  const htmlContent = await page.content();
  console.log(`页面HTML长度: ${htmlContent.length} 字符`);

  // 检查app元素
  const appContent = await page.evaluate(() => {
    const app = document.getElementById('app');
    if (!app) return { exists: false };
    return {
      exists: true,
      innerHTML: app.innerHTML.substring(0, 500),
      childCount: app.children.length,
      className: app.className,
    };
  });
  console.log(`#app元素: ${JSON.stringify(appContent, null, 2)}`);

  // 检查所有script标签
  const scripts = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('script')).map(s => ({
      src: s.src,
      innerHTML: s.innerHTML ? s.innerHTML.substring(0, 100) : '',
    }));
  });
  console.log('\nScript标签:');
  scripts.forEach((s, i) => console.log(`  ${i + 1}. src="${s.src}", inner="${s.innerHTML}"`));

  // 检查所有link标签（样式表）
  const stylesheets = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('link')).map(l => ({
      href: l.href,
      rel: l.rel,
    }));
  });
  console.log('\n样式表链接:');
  stylesheets.forEach((s, i) => console.log(`  ${i + 1}. href="${s.href}", rel="${s.rel}"`));

  // 4. 获取首页截图
  await page.screenshot({ path: 'test-homepage-full.png', fullPage: true });
  console.log('\n首页完整截图已保存: test-homepage-full.png');

  // 5. 测试子路由
  console.log('\n--- 子路由直接访问测试 ---');
  const subRoutes = ['/rooms', '/schedules', '/statistics'];
  for (const route of subRoutes) {
    const url = BASE_URL + route;
    console.log(`\n访问: ${url}`);

    // 清空请求记录
    failedRequests.length = 0;
    successfulRequests.length = 0;

    try {
      const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      const finalUrl = page.url();
      const status = response.status();

      console.log(`  HTTP状态: ${status}`);
      console.log(`  最终URL: ${finalUrl}`);

      if (failedRequests.length > 0) {
        console.log(`  失败请求: ${failedRequests.length}个`);
        failedRequests.slice(0, 10).forEach(r => console.log(`    [${r.status}] ${r.url}`));
      }

      // 截图
      const screenshotName = `test-route-${route.replace('/', '')}.png`;
      await page.screenshot({ path: screenshotName, fullPage: true });
      console.log(`  截图: ${screenshotName}`);

      // 获取页面文本内容
      const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 500));
      console.log(`  页面文本: ${bodyText}`);

    } catch (error) {
      console.log(`  访问失败: ${error.message}`);
    }
  }

  // 6. 检查404页面
  console.log('\n--- 检查404.html重定向机制 ---');
  const redirectPath = await page.evaluate(() => {
    return sessionStorage.getItem('redirect-path');
  });
  console.log(`sessionStorage中的redirect-path: ${redirectPath}`);

  const pageContent = await page.evaluate(() => document.body.innerHTML);
  console.log(`页面body内容 (前200字符): ${pageContent.substring(0, 200)}`);

  await browser.close();
  console.log('\n========== 深度分析完成 ==========');
}

deepAnalysis().catch(console.error);
