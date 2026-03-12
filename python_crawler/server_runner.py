#!/usr/bin/env python
"""
Amazon Crawler - 服务器运行脚本
支持日志记录、错误处理、定时任务
"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.crawler import AmazonCrawler
from src.search_crawler import AmazonSearchCrawler


def setup_logging(log_dir: Path = Path("logs")):
    """配置日志系统"""
    log_dir.mkdir(exist_ok=True)

    # 生成日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"crawler_{timestamp}.log"

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )

    return logging.getLogger(__name__)


def run_best_servers(
    pages: int = 1,
    products: int = 10,
    output: str | None = None,
):
    """运行 Best Sellers 爬虫"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Amazon Best Sellers Crawler - Server Mode")
    logger.info("=" * 60)

    # 生成输出文件名
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"output/bestsellers_{timestamp}.csv"

    # 创建爬虫
    crawler = AmazonCrawler(
        max_pages=pages,
        max_products=products,
        headless=True,  # 服务器模式强制无头
    )

    # 运行爬虫
    try:
        crawler.crawl()
        crawler.save_csv(output)
        logger.info(f"✅ 成功保存: {output}")
        return True
    except Exception as e:
        logger.error(f"❌ 爬取失败: {e}")
        return False


def run_search_server(
    keyword: str,
    pages: int = 1,
    products: int = 10,
    sort_by: str = "relevance",
    output: str | None = None,
):
    """运行搜索爬虫"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"Amazon Search Crawler - Keyword: {keyword}")
    logger.info("=" * 60)

    # 生成输出文件名
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = keyword.replace(" ", "_")[:30]
        output = f"output/search_{safe_keyword}_{timestamp}.csv"

    # 创建爬虫
    crawler = AmazonSearchCrawler(
        keyword=keyword,
        max_pages=pages,
        max_products=products,
        sort_by=sort_by,
        headless=True,  # 服务器模式强制无头
    )

    # 运行爬虫
    try:
        crawler.crawl()
        crawler.save_csv(output)
        logger.info(f"✅ 成功保存: {output}")
        return True
    except Exception as e:
        logger.error(f"❌ 爬取失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Amazon Crawler - Server Deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 模式选择
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--bestsellers",
        action="store_true",
        help="运行 Best Sellers 爬虫",
    )
    mode_group.add_argument(
        "--search",
        type=str,
        metavar="KEYWORD",
        help="运行搜索爬虫",
    )

    # 通用参数
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="抓取页数 (默认: 1)",
    )
    parser.add_argument(
        "--products",
        type=int,
        default=10,
        help="每页商品数 (默认: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件名",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="日志目录 (默认: logs)",
    )

    # 搜索模式参数
    parser.add_argument(
        "--sort",
        type=str,
        default="relevance",
        choices=["relevance", "price-asc", "price-desc", "review-rank", "date-desc"],
        help="排序方式 (默认: relevance)",
    )

    args = parser.parse_args()

    # 设置日志
    log_dir = Path(args.log_dir)
    logger = setup_logging(log_dir)

    # 运行爬虫
    success = False

    if args.bestellers:
        success = run_best_servers(
            pages=args.pages,
            products=args.products,
            output=args.output,
        )
    elif args.search:
        success = run_search_server(
            keyword=args.search,
            pages=args.pages,
            products=args.products,
            sort_by=args.sort,
            output=args.output,
        )

    # 返回状态码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
