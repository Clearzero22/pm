# 亚马逊数据采集浏览器插件开发指南

> 完整的开发指南，从零开始构建亚马逊数据采集插件

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术栈选择](#2-技术栈选择)
3. [插件基础架构](#3-插件基础架构)
4. [核心功能开发](#4-核心功能开发)
5. [数据提取策略](#5-数据提取策略)
6. [反爬虫应对](#6-反爬虫应对)
7. [数据存储方案](#7-数据存储方案)
8. [完整代码示例](#8-完整代码示例)
9. [部署与使用](#9-部署与使用)

---

## 1. 项目概述

### 1.1 功能定位

```
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon Scraper Extension                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  核心功能:                                                        │
│  ✅ 产品列表页采集 - 批量抓取搜索结果                             │
│  ✅ 产品详情页采集 - 提取完整产品信息                             │
│  ✅ 评论数据采集 - 支持翻页批量获取                               │
│  ✅ 竞品分析 - 对比多个ASIN数据                                  │
│  ✅ 数据导出 - Excel/CSV/JSON格式                                │
│  ✅ 云端同步 - 可选的后端存储                                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 采集数据字段

```yaml
产品基础信息:
  - ASIN: 亚马逊标准识别码
  - 标题: 产品名称
  - 品牌: 品牌名称
  - 价格: 当前价格、原价、折扣
  - 评分: 平均评分
  - 评论数: 总评论数量
  - BSR排名: 类目销售排名
  - 图片: 主图、附图URL

产品详情:
  - 描述: 产品描述
  - 五点描述: 卖点列表
  - 规格参数: 尺寸、重量等
  - 类目路径: 所属类目
  - 变体信息: 颜色、尺寸等变体

评论数据:
  - 评论标题
  - 评论内容
  - 评分
  - 评论日期
  - 评论者信息
  - 有用投票数

运营数据:
  - 卖家信息: FBA/FBM
  - 配送信息
  - 库存状态
  - 促销信息
```

---

## 2. 技术栈选择

### 2.1 推荐技术栈

```
┌─────────────────────────────────────────────────────────────┐
│                      技术栈选型                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  开发语言: TypeScript                                        │
│  原因:                                                        │
│    - 类型安全，减少运行时错误                                │
│    - 优秀的IDE支持                                          │
│    - 易于维护大型项目                                        │
│                                                              │
│  构建工具: Vite + CRXJS                                       │
│  原因:                                                        │
│    - 快速的热更新                                            │
│    - 原生ES模块支持                                          │
│    - 优秀的开发体验                                          │
│                                                              │
│  UI框架: React + TailwindCSS                                 │
│  原因:                                                        │
│    - 组件化开发                                              │
│    - 丰富的生态系统                                          │
│    - 快速UI开发                                              │
│                                                              │
│  数据处理: Cheerio / DOMParser                               │
│  原因:                                                        │
│    - 服务端渲染的HTML解析                                    │
│    - 轻量级                                                  │
│    - jQuery-like API                                         │
│                                                              │
│  数据存储:                                                   │
│    - IndexedDB: 本地大量数据存储                             │
│    - Chrome Storage: 配置和轻量数据                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 项目初始化

```bash
# 创建项目
npm create vite@latest amazon-scraper -- --template react-ts

# 进入目录
cd amazon-scraper

# 安装依赖
npm install

# 安装CRXJS（Chrome扩展插件开发工具）
npm install @crxjs/vite-plugin -D

# 安装其他依赖
npm install @types/chrome cheerio tailwindcss
npm install lucide-react clsx tailwind-merge

# 初始化Tailwind
npx tailwindcss init -p
```

---

## 3. 插件基础架构

### 3.1 Chrome插件核心组件

```
Amazon Scraper Extension
│
├── manifest.json           # 配置清单（插件身份证）
│
├── popup/                  # 弹窗界面
│   ├── popup.html         # 弹窗HTML
│   ├── popup.tsx          # 弹窗组件
│   └── style.css          # 样式
│
├── content/               # 内容脚本（注入页面）
│   ├── content.ts         # 主要采集逻辑
│   └── inject.ts          # 页面脚本
│
├── background/            # 后台脚本
│   └── background.ts      # 长期运行的服务
│
├── options/               # 设置页面
│   ├── options.html
│   └── options.tsx
│
├── assets/                # 静态资源
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
│
└── utils/                 # 工具函数
    ├── extractor.ts       # 数据提取
    ├── storage.ts         # 存储管理
    └── exporter.ts        # 数据导出
```

### 3.2 Manifest配置

```json
// manifest.json
{
  "manifest_version": 3,
  "name": "Amazon Product Scraper",
  "version": "1.0.0",
  "description": "采集亚马逊产品数据的浏览器插件",
  "permissions": [
    "storage",
    "activeTab",
    "scripting"
  ],
  "host_permissions": [
    "https://www.amazon.com/*",
    "https://www.amazon.co.uk/*",
    "https://www.amazon.de/*",
    "https://www.amazon.jp/*"
  ],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "assets/icon16.png",
      "48": "assets/icon48.png",
      "128": "assets/icon128.png"
    }
  },
  "background": {
    "service_worker": "background/background.js"
  },
  "content_scripts": [
    {
      "matches": [
        "https://www.amazon.com/*",
        "https://www.amazon.co.uk/*",
        "https://www.amazon.de/*",
        "https://www.amazon.jp/*"
      ],
      "js": ["content/content.js"],
      "run_at": "document_idle"
    }
  ],
  "options_page": "options/options.html",
  "icons": {
    "16": "assets/icon16.png",
    "48": "assets/icon48.png",
    "128": "assets/icon128.png"
  }
}
```

### 3.3 Vite配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { crx } from '@crxjs/vite-plugin'
import manifest from './manifest.json'

export default defineConfig({
  plugins: [
    react(),
    crx({ manifest }),
  ],
  build: {
    rollupOptions: {
      input: {
        popup: 'popup/popup.html',
        options: 'options/options.html',
      }
    }
  }
})
```

---

## 4. 核心功能开发

### 4.1 Content Script - 数据采集核心

```typescript
// content/content.ts

class AmazonScraper {
  private currentUrl: string = '';
  private pageType: 'search' | 'product' | 'review' | 'unknown' = 'unknown';

  constructor() {
    this.init();
  }

  private init() {
    // 监听URL变化（SPA页面）
    this.observeUrlChanges();

    // 监听来自popup的消息
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.action === 'scrape') {
        const data = this.scrapeCurrentPage();
        sendResponse({ success: true, data });
      }
    });

    // 通知background script页面已加载
    this.notifyPageLoad();
  }

  private observeUrlChanges() {
    let lastUrl = location.href;
    new MutationObserver(() => {
      const currentUrl = location.href;
      if (currentUrl !== lastUrl) {
        lastUrl = currentUrl;
        this.currentUrl = currentUrl;
        this.pageType = this.detectPageType();
        this.notifyPageLoad();
      }
    }).observe(document.body, { childList: true, subtree: true });
  }

  private detectPageType(): 'search' | 'product' | 'review' | 'unknown' {
    const url = window.location.href;

    // 搜索结果页
    if (url.includes('/s?k=') || url.includes('/s?field-keywords=')) {
      return 'search';
    }

    // 产品详情页
    const asinMatch = url.match(/\/dp\/([A-Z0-9]{10})/i);
    if (asinMatch) {
      return 'product';
    }

    // 评论页
    if (url.includes('/product-reviews/')) {
      return 'review';
    }

    return 'unknown';
  }

  private notifyPageLoad() {
    chrome.runtime.sendMessage({
      action: 'pageLoaded',
      url: this.currentUrl,
      pageType: this.pageType,
      asin: this.extractASIN()
    });
  }

  private extractASIN(): string | null {
    // 从URL提取ASIN
    const urlMatch = window.location.href.match(/\/dp\/([A-Z0-9]{10})/i);
    if (urlMatch) return urlMatch[1];

    // 从DOM提取ASIN
    const asinElement = document.querySelector('#ASIN, [data-asin]');
    if (asinElement) {
      return asinElement.getAttribute('value') || asinElement.getAttribute('data-asin');
    }

    return null;
  }

  // ========== 核心采集方法 ==========

  public scrapeCurrentPage() {
    switch (this.pageType) {
      case 'search':
        return this.scrapeSearchResults();
      case 'product':
        return this.scrapeProductDetails();
      case 'review':
        return this.scrapeReviews();
      default:
        return { error: 'Unknown page type' };
    }
  }

  // ========== 搜索结果页采集 ==========

  private scrapeSearchResults() {
    const products: ProductData[] = [];

    // Amazon搜索结果的容器
    const productContainers = document.querySelectorAll('[data-component-type="s-search-result"]');

    productContainers.forEach((container) => {
      const product = this.extractProductFromCard(container);
      if (product.asin) {
        products.push(product);
      }
    });

    return {
      type: 'search_results',
      url: window.location.href,
      keyword: this.extractSearchKeyword(),
      timestamp: Date.now(),
      products,
      total: products.length
    };
  }

  private extractProductFromCard(container: Element): ProductData {
    // ASIN
    const asin = container.getAttribute('data-asin') || '';

    // 标题
    const titleEl = container.querySelector('h2 a span');
    const title = titleEl?.textContent?.trim() || '';

    // 价格
    const priceEl = container.querySelector('.a-price .a-offscreen');
    const price = priceEl?.textContent?.trim() || '';
    const priceValue = this.parsePrice(price);

    // 评分
    const ratingEl = container.querySelector('i.a-icon-star-small span');
    const rating = ratingEl?.textContent?.trim() || '';

    // 评论数
    const reviewCountEl = container.querySelector('a span.a-size-base');
    const reviewCount = this.parseNumber(reviewCountEl?.textContent || '');

    // 链接
    const linkEl = container.querySelector('h2 a');
    const productUrl = linkEl?.getAttribute('href') || '';

    // 图片
    const imgEl = container.querySelector('.s-image');
    const image = imgEl?.getAttribute('src') || '';

    // 品牌
    const brandEl = container.querySelector('.a-size-base-plus.a-color-base');
    const brand = brandEl?.textContent?.trim() || '';

    // BSR排名
    const bsrEl = container.querySelector('.a-size-base.a-color-price');
    const bsr = bsrEl?.textContent?.trim() || '';

    return {
      asin,
      title,
      price,
      priceValue,
      currency: this.detectCurrency(price),
      rating,
      reviewCount,
      productUrl: `https://www.amazon.com${productUrl}`,
      image,
      brand,
      bsr
    };
  }

  // ========== 产品详情页采集 ==========

  private scrapeProductDetails() {
    const asin = this.extractASIN();

    if (!asin) {
      return { error: 'Cannot extract ASIN' };
    }

    return {
      type: 'product_details',
      asin,
      url: window.location.href,
      timestamp: Date.now(),
      ...this.extractProductInfo()
    };
  }

  private extractProductInfo() {
    // 标题
    const title = document.getElementById('productTitle')?.textContent?.trim() || '';

    // 价格
    const priceData = this.extractPriceData();

    // 品牌
    const brand = document.getElementById('bylineInfo')?.textContent?.trim()
      .replace(/Brand:|by/gi, '').trim() || '';

    // 评分
    const rating = document.querySelector('[data-hook="average-star-rating"] .a-icon-alt')
      ?.textContent?.match(/[\d.]+/)?.[0] || '';

    // 评论数
    const reviewCount = this.parseNumber(
      document.querySelector('[data-hook="total-review-count"]')?.textContent || ''
    );

    // BSR排名
    const bsrInfo = this.extractBSRInfo();

    // 图片
    const images = this.extractProductImages();

    // 五点描述
    const bulletPoints = this.extractBulletPoints();

    // 描述
    const description = this.extractDescription();

    // 规格参数
    const specifications = this.extractSpecifications();

    // 变体信息
    const variants = this.extractVariants();

    return {
      title,
      brand,
      price: priceData.price,
      originalPrice: priceData.originalPrice,
      currency: priceData.currency,
      discount: priceData.discount,
      rating,
      reviewCount,
      bsr: bsrInfo,
      images,
      bulletPoints,
      description,
      specifications,
      variants,
      inStock: this.checkStockStatus()
    };
  }

  private extractPriceData() {
    // 主价格
    const priceEl = document.querySelector('.a-price .a-offscreen');
    const price = priceEl?.textContent?.trim() || '';

    // 原价（划线价）
    const originalPriceEl = document.querySelector('.a-price.a-text-price .a-offscreen');
    const originalPrice = originalPriceEl?.textContent?.trim() || '';

    // 货币符号
    const currency = this.detectCurrency(price);

    // 计算折扣
    let discount = 0;
    if (price && originalPrice) {
      const priceValue = this.parsePrice(price);
      const originalValue = this.parsePrice(originalPrice);
      if (originalValue > 0) {
        discount = Math.round((1 - priceValue / originalValue) * 100);
      }
    }

    return { price, originalPrice, currency, discount };
  }

  private extractBSRInfo() {
    const bsrElements = document.querySelectorAll('#productDetails_detailBullets_sections1 tr');
    const bsrData: Record<string, string> = {};

    bsrElements.forEach((row) => {
      const label = row.querySelector('th')?.textContent?.trim();
      const value = row.querySelector('td')?.textContent?.trim();
      if (label && value) {
        bsrData[label] = value;
      }
    });

    return bsrData;
  }

  private extractProductImages() {
    const images: string[] = [];

    // 从ImageBlock数据中提取
    const imageBlockData = document.getElementById('imageBlock');
    if (imageBlockData) {
      const imgElements = imageBlockData.querySelectorAll('.a-spacing-small img');
      imgElements.forEach((img) => {
        const src = img.getAttribute('src') || img.getAttribute('data-src');
        if (src) {
          // 转换为高清图
          const hdUrl = this.convertToHDImage(src);
          images.push(hdUrl);
        }
      });
    }

    // 从altImages提取
    const altImages = document.getElementById('altImages');
    if (altImages) {
      const altImgElements = altImages.querySelectorAll('img');
      altImgElements.forEach((img) => {
        const src = img.getAttribute('src');
        if (src && !images.includes(src)) {
          images.push(this.convertToHDImage(src));
        }
      });
    }

    return [...new Set(images)]; // 去重
  }

  private convertToHDImage(url: string): string {
    // 转换为高清图片URL
    return url
      .replace(/\._.*_\.jpg$/, '._UL1500_.jpg')
      .replace(/\._.*_\.png$/, '._UL1500_.png');
  }

  private extractBulletPoints() {
    const bullets: string[] = [];

    const bulletElements = document.querySelectorAll('#feature-bullets ul li');
    bulletElements.forEach((el) => {
      const text = el.textContent?.trim();
      if (text && !text.includes('♦')) {
        bullets.push(text);
      }
    });

    return bullets;
  }

  private extractDescription() {
    // 从iframe中提取
    const iframe = document.getElementById('productDescription');
    if (iframe) {
      return iframe.textContent?.trim() || '';
    }

    // 从产品描述区域提取
    const descEl = document.getElementById('productDescription');
    if (descEl) {
      return descEl.textContent?.trim() || '';
    }

    return '';
  }

  private extractSpecifications() {
    const specs: Record<string, string> = {};

    // 从技术规格表格提取
    const techSpecs = document.getElementById('productDetails_techSpec_section_1');
    if (techSpecs) {
      const rows = techSpecs.querySelectorAll('tr');
      rows.forEach((row) => {
        const label = row.querySelector('th')?.textContent?.trim();
        const value = row.querySelector('td')?.textContent?.trim();
        if (label && value) {
          specs[label] = value;
        }
      });
    }

    return specs;
  }

  private extractVariants() {
    const variants: Record<string, string[]> = {};

    // 尺寸变体
    const sizeButtons = document.querySelectorAll('#variation_size_name .swatchSelect');
    const sizes: string[] = [];
    sizeButtons.forEach((btn) => {
      const text = btn.textContent?.trim();
      if (text) sizes.push(text);
    });
    if (sizes.length > 0) {
      variants['Size'] = sizes;
    }

    // 颜色变体
    const colorButtons = document.querySelectorAll('#variation_color_name .swatchSelect');
    const colors: string[] = [];
    colorButtons.forEach((btn) => {
      const text = btn.textContent?.trim();
      if (text) colors.push(text);
    });
    if (colors.length > 0) {
      variants['Color'] = colors;
    }

    return variants;
  }

  private checkStockStatus(): boolean {
    const stockEl = document.getElementById('availability');
    if (!stockEl) return true;

    const stockText = stockEl.textContent?.toLowerCase() || '';
    return !stockText.includes('unavailable') &&
           !stockText.includes('out of stock');
  }

  // ========== 评论采集 ==========

  private scrapeReviews() {
    const reviews: ReviewData[] = [];

    const reviewElements = document.querySelectorAll('[data-hook="review"]');

    reviewElements.forEach((reviewEl) => {
      const review = this.extractReviewData(reviewEl);
      reviews.push(review);
    });

    return {
      type: 'reviews',
      asin: this.extractASIN(),
      url: window.location.href,
      timestamp: Date.now(),
      reviews,
      total: reviews.length
    };
  }

  private extractReviewData(reviewEl: Element): ReviewData {
    // 评分
    const ratingEl = reviewEl.querySelector('[data-hook="review-star-rating"] span');
    const rating = ratingEl?.textContent?.match(/[\d.]+/)?.[0] || '';

    // 标题
    const titleEl = reviewEl.querySelector('[data-hook="review-title"] span');
    const title = titleEl?.textContent?.trim() || '';

    // 内容
    const bodyEl = reviewEl.querySelector('[data-hook="review-body"] span');
    const content = bodyEl?.textContent?.trim() || '';

    // 日期
    const dateEl = reviewEl.querySelector('[data-hook="review-date"]');
    const date = dateEl?.textContent?.trim() || '';

    // 评论者
    const authorEl = reviewEl.querySelector('.a-profile-name');
    const author = authorEl?.textContent?.trim() || '';

    // 有用投票数
    const helpfulEl = reviewEl.querySelector('[data-hook="helpful-vote-statement"]');
    const helpful = helpfulEl?.textContent?.match(/[\d,]+/)?.[0] || '0';

    return {
      rating,
      title,
      content,
      date,
      author,
      helpfulCount: this.parseNumber(helpful)
    };
  }

  // ========== 工具方法 ==========

  private parsePrice(priceStr: string): number {
    const match = priceStr.match(/[\d,]+\.?\d*/);
    if (match) {
      return parseFloat(match[0].replace(/,/g, ''));
    }
    return 0;
  }

  private parseNumber(str: string): number {
    const match = str.match(/[\d,]+/);
    if (match) {
      return parseInt(match[0].replace(/,/g, ''), 10);
    }
    return 0;
  }

  private detectCurrency(priceStr: string): string {
    if (priceStr.includes('€')) return 'EUR';
    if (priceStr.includes('£')) return 'GBP';
    if (priceStr.includes('¥')) return 'JPY';
    if (priceStr.includes('$') || priceStr.includes('US')) return 'USD';
    return 'USD';
  }

  private extractSearchKeyword(): string {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('k') || urlParams.get('field-keywords') || '';
  }
}

// 类型定义
interface ProductData {
  asin: string;
  title: string;
  price: string;
  priceValue?: number;
  currency: string;
  rating?: string;
  reviewCount?: number;
  productUrl: string;
  image: string;
  brand?: string;
  bsr?: string;
  discount?: number;
}

interface ReviewData {
  rating: string;
  title: string;
  content: string;
  date: string;
  author: string;
  helpfulCount: number;
}

// 初始化
const scraper = new AmazonScraper();

// 暴露给window（用于调试）
(window as any).amazonScraper = scraper;
```

### 4.2 Background Script - 后台服务

```typescript
// background/background.ts

interface ScrapeTask {
  id: string;
  type: 'single' | 'batch' | 'reviews';
  urls: string[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  results: any[];
  timestamp: number;
}

class BackgroundService {
  private tasks: Map<string, ScrapeTask> = new Map();

  constructor() {
    this.init();
  }

  private init() {
    // 监听插件安装
    chrome.runtime.onInstalled.addListener(() => {
      console.log('Amazon Scraper extension installed');
      this.createContextMenu();
    });

    // 监听消息
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // 保持消息通道开放
    });
  }

  private createContextMenu() {
    chrome.contextMenus.create({
      id: 'scrapeProduct',
      title: '采集产品数据',
      contexts: ['link', 'selection']
    });
  }

  private async handleMessage(
    message: any,
    sender: chrome.runtime.MessageSender,
    sendResponse: (response?: any) => void
  ) {
    switch (message.action) {
      case 'pageLoaded':
        await this.handlePageLoad(message);
        break;

      case 'scrape':
        const result = await this.handleScrapeRequest(message);
        sendResponse(result);
        break;

      case 'saveData':
        await this.saveData(message.data);
        sendResponse({ success: true });
        break;

      case 'getData':
        const data = await this.getData(message.key);
        sendResponse({ data });
        break;

      case 'exportData':
        await this.exportData(message.format, message.data);
        sendResponse({ success: true });
        break;
    }
  }

  private async handlePageLoad(message: any) {
    // 保存页面信息
    await chrome.storage.local.set({
      currentPage: {
        url: message.url,
        pageType: message.pageType,
        asin: message.asin
      }
    });

    // 更新图标徽章
    if (message.pageType === 'product') {
      chrome.action.setBadgeText({ text: 'P' });
      chrome.action.setBadgeTextColor({ color: '#4CAF50' });
    } else if (message.pageType === 'search') {
      chrome.action.setBadgeText({ text: 'S' });
      chrome.action.setBadgeTextColor({ color: '#2196F3' });
    } else {
      chrome.action.setBadgeText({ text: '' });
    }
  }

  private async handleScrapeRequest(message: any) {
    const tab = await this.getCurrentTab();
    if (!tab?.id) {
      return { success: false, error: 'No active tab' };
    }

    try {
      // 向content script发送消息
      const response = await chrome.tabs.sendMessage(tab.id, {
        action: 'scrape'
      });

      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  private async getCurrentTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab;
  }

  private async saveData(data: any) {
    // 保存到chrome.storage.local
    const existing = await chrome.storage.local.get('scrapedData');
    const scrapedData = existing.scrapedData || [];

    scrapedData.push({
      ...data,
      savedAt: Date.now()
    });

    await chrome.storage.local.set({ scrapedData });
  }

  private async getData(key: string) {
    const result = await chrome.storage.local.get(key);
    return result[key];
  }

  private async exportData(format: 'csv' | 'json' | 'excel', data: any[]) {
    let content: string;
    let filename: string;
    let mimeType: string;

    switch (format) {
      case 'json':
        content = JSON.stringify(data, null, 2);
        filename = `amazon-data-${Date.now()}.json`;
        mimeType = 'application/json';
        break;

      case 'csv':
        content = this.convertToCSV(data);
        filename = `amazon-data-${Date.now()}.csv`;
        mimeType = 'text/csv';
        break;

      case 'excel':
        // Excel需要使用第三方库，这里简化处理
        content = this.convertToCSV(data);
        filename = `amazon-data-${Date.now()}.csv`;
        mimeType = 'text/csv';
        break;
    }

    // 触发下载
    chrome.downloads.download({
      url: `data:${mimeType},${encodeURIComponent(content)}`,
      filename,
      saveAs: true
    });
  }

  private convertToCSV(data: any[]): string {
    if (!data.length) return '';

    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];

    for (const row of data) {
      const values = headers.map(header => {
        const value = row[header];
        const stringValue = typeof value === 'object'
          ? JSON.stringify(value)
          : String(value || '');
        return `"${stringValue.replace(/"/g, '""')}"`;
      });
      csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
  }
}

// 初始化
const backgroundService = new BackgroundService();
```

### 4.3 Popup - 弹窗界面

```typescript
// popup/popup.tsx

import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import './popup.css';

interface PageData {
  url: string;
  pageType: string;
  asin?: string;
}

interface ScrapedData {
  type: string;
  [key: string]: any;
}

function Popup() {
  const [pageData, setPageData] = useState<PageData | null>(null);
  const [isScraping, setIsScraping] = useState(false);
  const [scrapedData, setScrapedData] = useState<ScrapedData | null>(null);
  const [savedCount, setSavedCount] = useState(0);

  useEffect(() => {
    loadPageData();
    loadSavedData();
  }, []);

  const loadPageData = async () => {
    const result = await chrome.storage.local.get('currentPage');
    if (result.currentPage) {
      setPageData(result.currentPage);
    }
  };

  const loadSavedData = async () => {
    const result = await chrome.storage.local.get('scrapedData');
    const data = result.scrapedData || [];
    setSavedCount(data.length);
  };

  const handleScrape = async () => {
    setIsScraping(true);

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      const response = await chrome.tabs.sendMessage(tab.id!, {
        action: 'scrape'
      });

      if (response.success) {
        setScrapedData(response.data);

        // 自动保存
        await chrome.runtime.sendMessage({
          action: 'saveData',
          data: response.data
        });

        setSavedCount(prev => prev + 1);
      }
    } catch (error) {
      console.error('Scrape failed:', error);
      alert('采集失败: ' + (error as Error).message);
    } finally {
      setIsScraping(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    await chrome.runtime.sendMessage({
      action: 'exportData',
      format,
      key: 'scrapedData'
    });
  };

  const renderPageInfo = () => {
    if (!pageData) {
      return <div className="info-box">请在亚马逊页面上使用此插件</div>;
    }

    const icons = {
      product: '📦',
      search: '🔍',
      review: '⭐',
      unknown: '❓'
    };

    return (
      <div className="info-box">
        <div className="page-icon">{icons[pageData.pageType as keyof typeof icons]}</div>
        <div className="page-type">{getPageTypeName(pageData.pageType)}</div>
        {pageData.asin && (
          <div className="asin">ASIN: {pageData.asin}</div>
        )}
      </div>
    );
  };

  const renderDataPreview = () => {
    if (!scrapedData) return null;

    return (
      <div className="data-preview">
        <h3>采集数据预览</h3>
        <pre>{JSON.stringify(scrapedData, null, 2)}</pre>
      </div>
    );
  };

  return (
    <div className="popup-container">
      <header className="popup-header">
        <h1>🛒 Amazon Scraper</h1>
      </header>

      {renderPageInfo()}

      <div className="actions">
        <button
          onClick={handleScrape}
          disabled={isScraping || !pageData}
          className="btn-primary"
        >
          {isScraping ? '采集中...' : '📥 采集数据'}
        </button>

        <button
          onClick={() => handleExport('csv')}
          disabled={savedCount === 0}
          className="btn-secondary"
        >
          📄 导出CSV
        </button>

        <button
          onClick={() => handleExport('json')}
          disabled={savedCount === 0}
          className="btn-secondary"
        >
          📋 导出JSON
        </button>
      </div>

      <div className="stats">
        <div className="stat-item">
          <span className="stat-label">已保存</span>
          <span className="stat-value">{savedCount}</span>
        </div>
      </div>

      {renderDataPreview()}
    </div>
  );
}

function getPageTypeName(type: string): string {
  const names: Record<string, string> = {
    product: '产品详情页',
    search: '搜索结果页',
    review: '评论页',
    unknown: '未知页面'
  };
  return names[type] || '未知页面';
}

const container = document.getElementById('root');
const root = createRoot(container!);
root.render(<Popup />);
```

---

## 5. 数据提取策略

### 5.1 选择器策略

```typescript
// utils/selectors.ts

export const AmazonSelectors = {
  // 产品详情页
  product: {
    title: '#productTitle',
    price: {
      current: '.a-price .a-offscreen',
      original: '.a-price.a-text-price .a-offscreen'
    },
    brand: '#bylineInfo',
    rating: '[data-hook="average-star-rating"] .a-icon-alt',
    reviewCount: '[data-hook="total-review-count"]',
    images: {
      main: '#landingImage',
      gallery: '#altImages img'
    },
    bullets: '#feature-bullets ul li',
    description: '#productDescription',
    bsr: '#productDetails_detailBullets_sections1 tr',
    variations: {
      size: '#variation_size_name .swatchSelect',
      color: '#variation_color_name .swatchSelect'
    },
    availability: '#availability'
  },

  // 搜索结果页
  search: {
    container: '[data-component-type="s-search-result"]',
    asin: '[data-asin]',
    title: 'h2 a span',
    price: '.a-price .a-offscreen',
    rating: 'i.a-icon-star-small span',
    reviewCount: 'a span.a-size-base',
    link: 'h2 a',
    image: '.s-image',
    brand: '.a-size-base-plus.a-color-base'
  },

  // 评论页
  review: {
    container: '[data-hook="review"]',
    rating: '[data-hook="review-star-rating"] span',
    title: '[data-hook="review-title"] span',
    body: '[data-hook="review-body"] span',
    date: '[data-hook="review-date"]',
    author: '.a-profile-name',
    helpful: '[data-hook="helpful-vote-statement"]'
  }
};
```

### 5.2 防反爬策略

```typescript
// utils/anti-bot.ts

export class AntiBot {
  private static delays = [1000, 1500, 2000, 2500];
  private static lastRequestTime = 0;

  /**
   * 随机延迟
   */
  static async randomDelay(min: number = 1000, max: number = 3000) {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  /**
   * 模拟人类行为 - 随机滚动
   */
  static async simulateScroll(element: Element = document.body) {
    const scrollHeight = element.scrollHeight;
    const scrollSteps = 5;
    const stepHeight = scrollHeight / scrollSteps;

    for (let i = 0; i < scrollSteps; i++) {
      element.scrollTop = stepHeight * (i + 1);
      await this.randomDelay(500, 1000);
    }
  }

  /**
   * 检测CAPTCHA
   */
  static detectCaptcha(): boolean {
    // 检测CAPTCHA相关元素
    const captchaForms = document.querySelectorAll('form[action*="captcha"]');
    const captchaTitles = document.body.textContent?.includes('CAPTCHA') ||
                         document.body.textContent?.includes('enter the characters');

    return captchaForms.length > 0 || !!captchaTitles;
  }

  /**
   * 检测被封禁
   */
  static detectBlocked(): boolean {
    const blockedIndicators = [
      'To discuss automated access',
      'Sorry, we just need to make sure',
      'Enter the characters you see below',
      'been blocked'
    ];

    return blockedIndicators.some(indicator =>
      document.body.textContent?.includes(indicator)
    );
  }

  /**
   * 请求限流
   */
  static async throttleRequest() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;

    if (timeSinceLastRequest < 2000) {
      const waitTime = 2000 - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }

    this.lastRequestTime = Date.now();
  }

  /**
   * 获取随机User-Agent
   */
  static getRandomUserAgent(): string {
    const userAgents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    ];
    return userAgents[Math.floor(Math.random() * userAgents.length)];
  }
}
```

### 5.3 数据验证与清洗

```typescript
// utils/data-validator.ts

export class DataValidator {
  /**
   * 验证ASIN格式
   */
  static isValidASIN(asin: string): boolean {
    return /^[A-Z0-9]{10}$/i.test(asin);
  }

  /**
   * 验证产品数据完整性
   */
  static validateProductData(data: any): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!data.asin || !this.isValidASIN(data.asin)) {
      errors.push('Invalid or missing ASIN');
    }

    if (!data.title || data.title.length < 5) {
      errors.push('Title is too short or missing');
    }

    if (!data.price && !data.priceValue) {
      errors.push('Price information missing');
    }

    if (data.rating && isNaN(parseFloat(data.rating))) {
      errors.push('Invalid rating format');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * 清洗文本数据
   */
  static cleanText(text: string): string {
    return text
      .replace(/\s+/g, ' ')  // 多个空格转单个
      .replace(/\n\s*\n/g, '\n')  // 多个换行转单个
      .trim();
  }

  /**
   * 清洗URL
   */
  static cleanUrl(url: string): string {
    const cleaned = url.split('?')[0];  // 移除查询参数
    return cleaned.startsWith('http') ? cleaned : `https://www.amazon.com${cleaned}`;
  }

  /**
   * 标准化价格
   */
  static normalizePrice(price: any): number {
    if (typeof price === 'number') return price;
    if (typeof price === 'string') {
      const match = price.match(/[\d,]+\.?\d*/);
      if (match) {
        return parseFloat(match[0].replace(/,/g, ''));
      }
    }
    return 0;
  }
}
```

---

## 6. 反爬虫应对

### 6.1 IP轮换（需要代理服务）

```typescript
// utils/proxy-manager.ts

export class ProxyManager {
  private proxies: string[] = [];
  private currentIndex = 0;

  constructor(proxies: string[]) {
    this.proxies = proxies;
  }

  /**
   * 获取下一个代理
   */
  getNextProxy(): string {
    const proxy = this.proxies[this.currentIndex];
    this.currentIndex = (this.currentIndex + 1) % this.proxies.length;
    return proxy;
  }

  /**
   * 移除失效代理
   */
  removeProxy(proxy: string) {
    this.proxies = this.proxies.filter(p => p !== proxy);
  }

  /**
   * 检查代理可用性
   */
  async checkProxy(proxy: string): Promise<boolean> {
    try {
      const response = await fetch('https://www.amazon.com', {
        method: 'HEAD',
        // @ts-ignore
        proxy: proxy
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}
```

### 6.2 会话管理

```typescript
// utils/session-manager.ts

interface SessionData {
  cookies: string;
  userAgent: string;
  lastUsed: number;
}

export class SessionManager {
  private static sessionKey = 'amazon_session';

  /**
   * 保存会话
   */
  static async saveSession(cookies: string, userAgent: string) {
    const session: SessionData = {
      cookies,
      userAgent,
      lastUsed: Date.now()
    };

    await chrome.storage.local.set({
      [this.sessionKey]: session
    });
  }

  /**
   * 获取会话
   */
  static async getSession(): Promise<SessionData | null> {
    const result = await chrome.storage.local.get(this.sessionKey);
    return result[this.sessionKey] || null;
  }

  /**
   * 检查会话是否过期
   */
  static isSessionExpired(session: SessionData, maxAge: number = 3600000): boolean {
    return Date.now() - session.lastUsed > maxAge;
  }

  /**
   * 清除会话
   */
  static async clearSession() {
    await chrome.storage.local.remove(this.sessionKey);
  }
}
```

### 6.3 请求频率控制

```typescript
// utils/rate-limiter.ts

export class RateLimiter {
  private requestTimes: number[] = [];
  private readonly maxRequests: number;
  private readonly timeWindow: number;

  constructor(maxRequests: number = 10, timeWindow: number = 60000) {
    this.maxRequests = maxRequests;
    this.timeWindow = timeWindow;
  }

  /**
   * 等待直到可以发送请求
   */
  async waitForSlot(): Promise<void> {
    const now = Date.now();

    // 清理过期的请求记录
    this.requestTimes = this.requestTimes.filter(
      time => now - time < this.timeWindow
    );

    // 如果达到限制，计算等待时间
    if (this.requestTimes.length >= this.maxRequests) {
      const oldestRequest = Math.min(...this.requestTimes);
      const waitTime = this.timeWindow - (now - oldestRequest);

      if (waitTime > 0) {
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }

    // 记录本次请求
    this.requestTimes.push(Date.now());
  }

  /**
   * 获取当前请求数
   */
  getCurrentRequestCount(): number {
    const now = Date.now();
    return this.requestTimes.filter(
      time => now - time < this.timeWindow
    ).length;
  }
}
```

---

## 7. 数据存储方案

### 7.1 IndexedDB封装

```typescript
// utils/database.ts

export class Database {
  private db: IDBDatabase | null = null;
  private readonly dbName = 'AmazonScraperDB';
  private readonly version = 1;

  async init() {
    return new Promise<void>((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // 创建产品表
        if (!db.objectStoreNames.contains('products')) {
          const productStore = db.createObjectStore('products', { keyPath: 'asin' });
          productStore.createIndex('timestamp', 'timestamp', { unique: false });
          productStore.createIndex('brand', 'brand', { unique: false });
        }

        // 创建评论表
        if (!db.objectStoreNames.contains('reviews')) {
          const reviewStore = db.createObjectStore('reviews', { keyPath: 'id', autoIncrement: true });
          reviewStore.createIndex('asin', 'asin', { unique: false });
        }

        // 创建搜索记录表
        if (!db.objectStoreNames.contains('searches')) {
          const searchStore = db.createObjectStore('searches', { keyPath: 'id', autoIncrement: true });
          searchStore.createIndex('keyword', 'keyword', { unique: false });
          searchStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  async addProduct(product: any) {
    return this.transaction('products', 'readwrite', (store) => {
      return store.put(product);
    });
  }

  async getProduct(asin: string) {
    return this.transaction('products', 'readonly', (store) => {
      return store.get(asin);
    });
  }

  async getAllProducts() {
    return this.transaction('products', 'readonly', (store) => {
      return store.getAll();
    });
  }

  async addReview(review: any) {
    return this.transaction('reviews', 'readwrite', (store) => {
      return store.add(review);
    });
  }

  async getReviewsByASIN(asin: string) {
    return this.transaction('reviews', 'readonly', (store) => {
      const index = store.index('asin');
      return index.getAll(asin);
    });
  }

  async addSearch(search: any) {
    return this.transaction('searches', 'readwrite', (store) => {
      return store.add(search);
    });
  }

  async clearStore(storeName: string) {
    return this.transaction(storeName, 'readwrite', (store) => {
      return store.clear();
    });
  }

  private transaction<T>(
    storeName: string,
    mode: IDBTransactionMode,
    callback: (store: IDBObjectStore) => IDBRequest<T>
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(storeName, mode);
      const store = transaction.objectStore(storeName);
      const request = callback(store);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
}

// 单例
export const db = new Database();
```

### 7.2 数据导出功能

```typescript
// utils/exporter.ts

import * as XLSX from 'xlsx';

export class DataExporter {
  /**
   * 导出为Excel
   */
  static async exportToExcel(data: any[], filename: string = 'amazon-data.xlsx') {
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Products');

    XLSX.writeFile(workbook, filename);
  }

  /**
   * 导出为CSV
   */
  static exportToCSV(data: any[], filename: string = 'amazon-data.csv') {
    const csv = this.convertToCSV(data);
    this.downloadFile(csv, filename, 'text/csv');
  }

  /**
   * 导出为JSON
   */
  static exportToJSON(data: any[], filename: string = 'amazon-data.json') {
    const json = JSON.stringify(data, null, 2);
    this.downloadFile(json, filename, 'application/json');
  }

  private static convertToCSV(data: any[]): string {
    if (!data.length) return '';

    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];

    for (const row of data) {
      const values = headers.map(header => {
        const value = row[header];
        const stringValue = typeof value === 'object'
          ? JSON.stringify(value)
          : String(value ?? '');
        return `"${stringValue.replace(/"/g, '""')}"`;
      });
      csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
  }

  private static downloadFile(content: string, filename: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * 生成数据报告
   */
  static generateReport(data: any[]): {
    total: number;
    byBrand: Record<string, number>;
    byPriceRange: Record<string, number>;
    avgRating: number;
  } {
    const report = {
      total: data.length,
      byBrand: {} as Record<string, number>,
      byPriceRange: {} as Record<string, number>,
      avgRating: 0
    };

    let totalRating = 0;
    let ratingCount = 0;

    for (const item of data) {
      // 按品牌统计
      if (item.brand) {
        report.byBrand[item.brand] = (report.byBrand[item.brand] || 0) + 1;
      }

      // 按价格区间统计
      const price = item.priceValue || 0;
      const priceRange = this.getPriceRange(price);
      report.byPriceRange[priceRange] = (report.byPriceRange[priceRange] || 0) + 1;

      // 评分统计
      if (item.rating) {
        totalRating += parseFloat(item.rating);
        ratingCount++;
      }
    }

    report.avgRating = ratingCount > 0 ? totalRating / ratingCount : 0;

    return report;
  }

  private static getPriceRange(price: number): string {
    if (price < 10) return '$0-10';
    if (price < 25) return '$10-25';
    if (price < 50) return '$25-50';
    if (price < 100) return '$50-100';
    if (price < 200) return '$100-200';
    return '$200+';
  }
}
```

---

## 8. 完整代码示例

### 8.1 package.json

```json
{
  "name": "amazon-scraper-extension",
  "version": "1.0.0",
  "description": "Amazon数据采集浏览器插件",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "cheerio": "^1.0.0-rc.12",
    "xlsx": "^0.18.5"
  },
  "devDependencies": {
    "@crxjs/vite-plugin": "^2.0.0-beta.18",
    "@types/chrome": "^0.0.245",
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```

### 8.2 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "types": ["chrome", "vite/client"]
  },
  "include": ["**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 9. 部署与使用

### 9.1 构建插件

```bash
# 开发模式
npm run dev

# 生产构建
npm run build

# 构建产物在 dist/ 目录
```

### 9.2 安装到浏览器

```
Chrome/Edge安装步骤:
┌─────────────────────────────────────────────────────────────┐
│ 1. 打开浏览器，输入: chrome://extensions/                   │
│ 2. 开启右上角的"开发者模式"                                  │
│ 3. 点击"加载已解压的扩展程序"                                │
│ 4. 选择项目的 dist/ 目录                                     │
│ 5. 插件安装完成                                              │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 使用指南

```
┌─────────────────────────────────────────────────────────────┐
│                      使用流程                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 打开亚马逊产品页面或搜索结果页                             │
│                                                              │
│  2. 点击浏览器工具栏中的插件图标                               │
│                                                              │
│  3. 查看页面类型识别结果                                      │
│     - 📦 = 产品详情页                                        │
│     - 🔍 = 搜索结果页                                        │
│                                                              │
│  4. 点击"采集数据"按钮                                        │
│                                                              │
│  5. 查看采集结果预览                                          │
│                                                              │
│  6. 点击导出按钮保存数据                                       │
│     - CSV格式: Excel可直接打开                                │
│     - JSON格式: 程序化处理                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 9.4 高级功能

#### 批量采集

```typescript
// 添加批量采集功能
async function batchScrape(urls: string[]) {
  const results = [];

  for (const url of urls) {
    // 打开新标签
    const tab = await chrome.tabs.create({ url, active: false });

    // 等待页面加载
    await new Promise(resolve => {
      chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
        if (tabId === tab.id && info.status === 'complete') {
          chrome.tabs.onUpdated.removeListener(listener);
          resolve(undefined);
        }
      });
    });

    // 采集数据
    const data = await scrapeTab(tab.id);
    results.push(data);

    // 关闭标签
    await chrome.tabs.remove(tab.id);

    // 延迟避免请求过快
    await delay(2000);
  }

  return results;
}
```

#### 自动翻页采集

```typescript
// 自动翻页采集评论
async function scrapeAllReviews(asin: string) {
  let allReviews: ReviewData[] = [];
  let pageNumber = 1;
  let hasNextPage = true;

  while (hasNextPage) {
    // 构建评论页URL
    const reviewUrl = `https://www.amazon.com/product-reviews/${asin}/reviewerType=all_reviews&pageNumber=${pageNumber}`;

    // 导航到评论页
    await chrome.tabs.update({ url: reviewUrl });

    // 等待页面加载
    await delay(3000);

    // 采集当前页评论
    const reviews = await scrapeCurrentPage();
    allReviews = allReviews.concat(reviews);

    // 检查是否有下一页
    hasNextPage = await checkNextPage();
    pageNumber++;
  }

  return allReviews;
}
```

### 9.5 注意事项

```
⚠️  重要提示:
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  1. 法律合规:                                                │
│     - 仅用于个人研究和学习                                    │
│     - 遵守亚马逊服务条款                                      │
│     - 不用于商业竞争或恶意爬取                                │
│                                                              │
│  2. 使用限制:                                                │
│     - 控制采集频率，避免对服务器造成压力                      │
│     - 同一IP每天建议不超过100次请求                           │
│     - 大量采集建议使用代理池                                  │
│                                                              │
│  3. 数据安全:                                                │
│     - 不要采集敏感个人信息                                    │
│     - 妥善保管采集的数据                                      │
│                                                              │
│  4. 维护更新:                                                │
│     - Amazon页面结构可能变化                                  │
│     - 需要定期更新选择器                                      │
│     - 建议添加错误上报功能                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 总结

本文档提供了完整的亚马逊数据采集浏览器插件开发指南，涵盖：

1. ✅ 完整的项目架构设计
2. ✅ 核心采集代码实现
3. ✅ 反爬虫应对策略
4. ✅ 数据存储与导出方案
5. ✅ 部署与使用说明

按照本指南，你可以构建一个功能完整的亚马逊数据采集插件。如有问题，欢迎反馈！

---

**文档版本:** v1.0
**最后更新:** 2026-03-12
**作者:** AI Development Team
