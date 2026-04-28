const { chromium } = require('@playwright/test');

const BASE_URL = 'https://nagato-yuki.github.io/smart-scheduler/';

const testResults = {
  homepageLoad: { status: 'PENDING', details: '' },
  navigation: [],
  javascriptErrors: [],
  styleIssues: [],
  directUrlAccess: [],
};

async function runTests() {
  console.log('========== 智能排课系统自动化测试开始 ==========\n');
  console.log(`测试目标: ${BASE_URL}\n`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'zh-CN',
  });

  const page = await context.newPage();

  // 收集控制台错误
  const consoleErrors = [];
  const consoleWarnings = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    } else if (msg.type() === 'warning') {
      consoleWarnings.push(msg.text());
    }
  });

  // 收集页面错误
  const pageErrors = [];
  page.on('pageerror', error => {
    pageErrors.push(error.message);
  });

  // =====================================================
  // 测试1: 访问首页，确认页面加载
  // =====================================================
  console.log('--- 测试1: 访问首页 ---');
  try {
    const response = await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000); // 等待Vue渲染

    const status = response.status();
    console.log(`HTTP状态码: ${status}`);

    const title = await page.title();
    console.log(`页面标题: ${title}`);

    // 检查侧边栏导航是否存在
    const sidebarExists = await page.locator('.el-aside, .sidebar, [class*="side"], [class*="menu"]').first().isVisible().catch(() => false);

    // 检查主内容区是否存在
    const mainContentExists = await page.locator('.el-main, .main, [class*="main"], [class*="content"]').first().isVisible().catch(() => false);

    // 检查是否有Element Plus的元素
    const elPlusExists = await page.locator('.el-menu, .el-button, .el-table').first().isVisible().catch(() => false);

    // 获取页面中的导航菜单项
    const menuItems = await page.locator('.el-menu-item').all();
    const menuTexts = [];
    for (const item of menuItems) {
      try {
        const text = await item.textContent();
        menuTexts.push(text.trim());
      } catch (e) {}
    }

    testResults.homepageLoad = {
      status: 'PASS',
      details: `HTTP状态: ${status}, 页面标题: "${title}", 侧边栏: ${sidebarExists}, 主内容: ${mainContentExists}, Element Plus组件: ${elPlusExists}`,
      menuItems: menuTexts,
    };

    console.log(`首页加载结果: ${testResults.homepageLoad.status}`);
    console.log(`  ${testResults.homepageLoad.details}`);
    console.log(`  导航菜单项: ${JSON.stringify(menuTexts)}`);

    // 截图
    await page.screenshot({ path: 'test-homepage.png', fullPage: true });
    console.log('  截图已保存: test-homepage.png');
  } catch (error) {
    testResults.homepageLoad = {
      status: 'FAIL',
      details: `首页加载失败: ${error.message}`,
    };
    console.log(`首页加载失败: ${error.message}`);
  }

  // =====================================================
  // 测试2: 依次点击每个导航菜单项
  // =====================================================
  console.log('\n--- 测试2: 导航菜单路由跳转 ---');

  const navItems = [
    { name: '首页', expectedPath: '/' },
    { name: '教室管理', expectedPath: '/rooms' },
    { name: '教师管理', expectedPath: '/teachers' },
    { name: '班级管理', expectedPath: '/classes' },
    { name: '课程管理', expectedPath: '/courses' },
    { name: '节假日管理', expectedPath: '/holidays' },
    { name: '数据导入', expectedPath: '/import' },
    { name: '课表查看', expectedPath: '/schedules' },
    { name: '课时统计', expectedPath: '/statistics' },
    { name: '调整课表', expectedPath: '/adjust-schedule' },
  ];

  // 先返回首页
  try {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
  } catch (e) {
    console.log('返回首页时出错，继续测试');
  }

  for (const navItem of navItems) {
    const result = { name: navItem.name, expectedPath: navItem.expectedPath, status: 'PENDING', details: '' };

    try {
      // 尝试点击菜单项
      const menuItems = await page.locator('.el-menu-item').all();
      let clicked = false;

      for (const item of menuItems) {
        try {
          const text = await item.textContent();
          if (text.trim().includes(navItem.name)) {
            await item.click();
            await page.waitForTimeout(2000);
            clicked = true;
            break;
          }
        } catch (e) {
          // 继续尝试下一个
        }
      }

      if (!clicked) {
        // 如果没找到，尝试直接访问URL
        const url = BASE_URL + (navItem.expectedPath === '/' ? '' : navItem.expectedPath);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(2000);
        result.status = 'DIRECT_NAVIGATION';
        result.details = `未找到菜单项，通过直接URL访问: ${url}`;
      } else {
        const currentUrl = page.url();
        const currentPath = new URL(currentUrl).pathname.replace('/smart-scheduler', '');
        result.status = 'PASS';
        result.details = `跳转成功，当前URL: ${currentUrl}`;
      }
    } catch (error) {
      result.status = 'FAIL';
      result.details = `跳转失败: ${error.message}`;
    }

    // 检查页面是否有错误显示
    try {
      const hasErrorText = await page.locator('text=404').isVisible().catch(() => false);
      if (hasErrorText) {
        result.status = 'FAIL';
        result.details += ' | 页面显示404错误';
      }
    } catch (e) {}

    testResults.navigation.push(result);
    console.log(`  [${result.status}] ${result.name}: ${result.details}`);
  }

  // =====================================================
  // 测试3: 检查控制台JavaScript错误
  // =====================================================
  console.log('\n--- 测试3: JavaScript错误检查 ---');

  // 重新访问几个主要页面来捕获错误
  const pagesToCheck = [
    BASE_URL,
    BASE_URL + 'rooms',
    BASE_URL + 'teachers',
    BASE_URL + 'schedules',
  ];

  for (const url of pagesToCheck) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2000);
    } catch (e) {
      testResults.javascriptErrors.push({ page: url, error: e.message });
    }
  }

  if (consoleErrors.length > 0) {
    testResults.javascriptErrors = consoleErrors;
    console.log(`  发现 ${consoleErrors.length} 个控制台错误:`);
    consoleErrors.forEach((err, i) => console.log(`    ${i + 1}. ${err}`));
  } else {
    testResults.javascriptErrors = [];
    console.log('  未发现JavaScript错误');
  }

  if (pageErrors.length > 0) {
    testResults.javascriptErrors.push(...pageErrors.map(e => ({ type: 'pageerror', message: e })));
    console.log(`  发现 ${pageErrors.length} 个页面错误:`);
    pageErrors.forEach((err, i) => console.log(`    ${i + 1}. ${err}`));
  }

  // =====================================================
  // 测试4: 检查页面样式
  // =====================================================
  console.log('\n--- 测试4: 页面样式检查 ---');

  try {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);

    // 检查样式表是否加载
    const stylesheets = await page.$$eval('link[rel="stylesheet"]', els => els.length);
    console.log(`  加载的样式表数量: ${stylesheets}`);

    // 检查内联样式
    const computedStyle = await page.evaluate(() => {
      const body = document.body;
      const style = window.getComputedStyle(body);
      return {
        fontFamily: style.fontFamily,
        backgroundColor: style.backgroundColor,
        margin: style.margin,
      };
    });
    console.log(`  页面样式: ${JSON.stringify(computedStyle)}`);

    // 检查是否有元素使用了fallback字体
    const elementPlusLoaded = await page.evaluate(() => {
      return document.querySelector('[class*="el-"]') !== null;
    });
    console.log(`  Element Plus组件加载: ${elementPlusLoaded}`);

    testResults.styleIssues = {
      status: elementPlusLoaded ? 'PASS' : 'WARNING',
      details: `样式表: ${stylesheets}, Element Plus: ${elementPlusLoaded}`,
    };
  } catch (error) {
    testResults.styleIssues = {
      status: 'FAIL',
      details: error.message,
    };
  }

  // =====================================================
  // 测试5: 测试直接访问子路由URL
  // =====================================================
  console.log('\n--- 测试5: 直接访问子路由URL ---');

  const urlsToTest = [
    { name: '首页', url: BASE_URL },
    { name: '教室管理', url: BASE_URL + 'rooms' },
    { name: '教师管理', url: BASE_URL + 'teachers' },
    { name: '班级管理', url: BASE_URL + 'classes' },
    { name: '课程管理', url: BASE_URL + 'courses' },
    { name: '节假日管理', url: BASE_URL + 'holidays' },
    { name: '数据导入', url: BASE_URL + 'import' },
    { name: '课表查看', url: BASE_URL + 'schedules' },
    { name: '课时统计', url: BASE_URL + 'statistics' },
    { name: '调整课表', url: BASE_URL + 'adjust-schedule' },
  ];

  for (const urlTest of urlsToTest) {
    const result = { name: urlTest.name, url: urlTest.url, status: 'PENDING', details: '' };

    try {
      const response = await page.goto(urlTest.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2000);

      const finalUrl = page.url();
      const httpStatus = response.status();

      // 检查是否被正确重定向（404.html -> index.html）
      const redirected = finalUrl !== urlTest.url;

      // 检查页面是否有Vue应用挂载
      const vueAppExists = await page.locator('#app').isVisible().catch(() => false);
      const elMenuExists = await page.locator('.el-menu').isVisible().catch(() => false);

      // 检查是否有404文本
      const has404 = await page.locator('text=/404|Not Found|页面不存在/').first().isVisible().catch(() => false);

      if (has404) {
        result.status = 'FAIL';
        result.details = `页面显示404错误`;
      } else if (!vueAppExists && !elMenuExists) {
        result.status = 'WARNING';
        result.details = `页面可能未正确加载Vue应用，HTTP: ${httpStatus}, 最终URL: ${finalUrl}`;
      } else {
        result.status = 'PASS';
        result.details = `加载成功，HTTP: ${httpStatus}${redirected ? ', 经历了重定向' : ''}`;
      }
    } catch (error) {
      result.status = 'FAIL';
      result.details = `访问失败: ${error.message}`;
    }

    testResults.directUrlAccess.push(result);
    console.log(`  [${result.status}] ${result.name}: ${result.details}`);
  }

  await browser.close();

  // =====================================================
  // 输出测试报告
  // =====================================================
  console.log('\n\n========================================');
  console.log('          测试结果汇总');
  console.log('========================================\n');

  console.log(`1. 首页加载: [${testResults.homepageLoad.status}] ${testResults.homepageLoad.details}`);
  if (testResults.homepageLoad.menuItems) {
    console.log(`   导航菜单项: ${testResults.homepageLoad.menuItems.join(', ')}`);
  }

  console.log('\n2. 导航菜单路由跳转:');
  testResults.navigation.forEach(item => {
    console.log(`   [${item.status}] ${item.name} -> ${item.expectedPath}: ${item.details}`);
  });

  console.log('\n3. JavaScript错误:');
  if (testResults.javascriptErrors.length === 0) {
    console.log('   无错误');
  } else {
    testResults.javascriptErrors.forEach((err, i) => {
      console.log(`   ${i + 1}. ${typeof err === 'string' ? err : JSON.stringify(err)}`);
    });
  }

  console.log('\n4. 页面样式:');
  console.log(`   [${testResults.styleIssues.status}] ${testResults.styleIssues.details}`);

  console.log('\n5. 直接访问子路由URL:');
  testResults.directUrlAccess.forEach(item => {
    console.log(`   [${item.status}] ${item.name} (${item.url}): ${item.details}`);
  });

  // 保存详细报告到文件
  const fs = require('fs');
  const report = JSON.stringify(testResults, null, 2);
  fs.writeFileSync('test-results.json', report, 'utf-8');
  console.log('\n详细测试结果已保存到: test-results.json');

  console.log('\n========================================');
  console.log('          测试完成');
  console.log('========================================');
}

runTests().catch(error => {
  console.error('测试执行过程中发生错误:', error);
  process.exit(1);
});
