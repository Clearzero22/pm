#!/usr/bin/env python3
"""Feishu Bitable Sync Module for Amazon Crawler.

Sync Amazon product data to Feishu Bitable.
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


class FeishuSync:
    """Sync Amazon crawler data to Feishu Bitable."""

    def __init__(self, config_path: str = None):
        """Initialize Feishu sync client.

        Args:
            config_path: Path to config file (optional)
        """
        self.config = self._load_config(config_path)
        self.api_base = "https://open.feishu.cn/open-apis"

    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from environment or config file."""
        # Try environment variables first
        config = {
            "app_id": os.getenv("FEISHU_APP_ID", ""),
            "app_secret": os.getenv("FEISHU_APP_SECRET", ""),
            "app_token": os.getenv("FEISHU_BITABLE_APP_TOKEN", ""),
            "table_id": os.getenv("FEISHU_TABLE_ID", ""),
        }

        # Try config file if environment variables not set
        if not all(config.values()):
            config_paths = [
                config_path or "",
                "config/feishu_config.yaml",
                ".feishu_config.json",
            ]
            for path in config_paths:
                if path and Path(path).exists():
                    config.update(self._load_config_file(path))
                    break

        return config

    def _load_config_file(self, path: str) -> Dict:
        """Load config from YAML or JSON file."""
        path = Path(path)
        try:
            if path.suffix == ".json":
                import json
                return json.loads(path.read_text())
            elif path.suffix in [".yaml", ".yml"]:
                import yaml
                return yaml.safe_load(path.read_text())
        except ImportError:
            return {}

    def sync_csv(self, csv_path: str) -> Dict[str, Any]:
        """Sync CSV data to Feishu Bitable.

        Args:
            csv_path: Path to CSV file

        Returns:
            Sync result with statistics
        """
        if not Path(csv_path).exists():
            return {"error": f"CSV file not found: {csv_path}"}

        # Check configuration
        if not self._validate_config():
            return {"error": "Feishu configuration incomplete. Please set environment variables or config file."}

        # Load CSV data
        df = pd.read_csv(csv_path)

        # Transform data
        records = self._transform_data(df)

        # Batch write
        result = self._batch_write(records)

        return result

    def _validate_config(self) -> bool:
        """Validate required configuration."""
        required = ["app_id", "app_secret", "app_token", "table_id"]
        return all(self.config.get(k) for k in required)

    def _transform_data(self, df: pd.DataFrame) -> List[Dict]:
        """Transform DataFrame to Feishu records.

        Args:
            df: Input DataFrame

        Returns:
            List of Feishu records
        """
        records = []

        for _, row in df.iterrows():
            record = {
                "fields": {
                    "ASIN": str(row.get("asin", "")),
                    "商品标题": str(row.get("title", ""))[:500],  # Truncate long titles
                    "价格": self._extract_price(row.get("price", "")),
                    "评分": self._extract_rating(row.get("rating", "")),
                    "商品描述": str(row.get("description", ""))[:2000],
                    "商品链接": str(row.get("url", "")),
                    "采集时间": pd.Timestamp.now().isoformat(),
                }
            }
            records.append(record)

        return records

    def _extract_price(self, price_str: str) -> float:
        """Extract numeric price from string."""
        import re
        match = re.search(r'[\d,]+\.?\d*', str(price_str))
        if match:
            return float(match.group().replace(',', ''))
        return 0.0

    def _extract_rating(self, rating_str: str) -> float:
        """Extract numeric rating from string."""
        import re
        match = re.search(r'([\d.]+)', str(rating_str))
        if match:
            return float(match.group(1))
        return 0.0

    def _batch_write(self, records: List[Dict], batch_size: int = 50) -> Dict[str, Any]:
        """Batch write records to Feishu.

        Args:
            records: List of records to write
            batch_size: Batch size for API calls (max 1000 per Feishu API)

        Returns:
            Write result statistics
        """
        total = len(records)
        success = 0
        failed = 0
        errors = []

        print(f"\n=== 飞书多维表格同步 ===")
        print(f"配置检查:")
        print(f"  - App ID: {self.config['app_id'][:10]}...")
        print(f"  - App Token: {self.config['app_token'][:10]}...")
        print(f"  - Table ID: {self.config['table_id'][:10]}...")
        print(f"\n准备同步 {total} 条记录...")

        # Get tenant access token
        token = self._get_tenant_access_token()
        if not token:
            return {"total": total, "success": 0, "failed": total, "errors": ["Failed to get access token"]}

        # Batch write (max 500 per batch for safety, Feishu limit is 1000)
        actual_batch_size = min(batch_size, 500)
        for i in range(0, total, actual_batch_size):
            batch = records[i:i + actual_batch_size]
            print(f"  批次 {i//actual_batch_size + 1}: {len(batch)} 条记录...", end="")

            result = self._api_call(token, batch)

            if result.get("success"):
                success += len(batch)
                print(" ✓")
            else:
                failed += len(batch)
                errors.append(result.get("error", "Unknown error"))
                print(f" ✗ ({result.get('error', 'Unknown error')})")

            # Rate limiting: Feishu allows 50 requests/second
            # Add small delay to avoid hitting rate limits
            import time
            time.sleep(0.05)

        print(f"\n✓ 同步完成: {success} 条成功, {failed} 条失败")

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "errors": errors,
        }

    def _get_tenant_access_token(self) -> str:
        """Get tenant access token from Feishu API.

        Returns:
            Access token string or empty string on failure
        """
        import requests

        url = f"{self.api_base}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": self.config["app_id"],
            "app_secret": self.config["app_secret"],
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 0:
                return result.get("tenant_access_token", "")
            else:
                print(f"  获取 Token 失败: {result.get('msg', 'Unknown error')}")
                return ""
        except Exception as e:
            print(f"  获取 Token 异常: {e}")
            return ""

    def _api_call(self, token: str, records: List[Dict]) -> Dict:
        """Make actual Feishu API call to batch create records.

        Args:
            token: Tenant access token
            records: List of records to create

        Returns:
            Result dict with 'success' boolean and optional 'error' message
        """
        import requests

        url = f"{self.api_base}/bitable/v1/apps/{self.config['app_token']}/tables/{self.config['table_id']}/records/batch_create"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        data = {"records": records}

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            result = response.json()

            if result.get("code") == 0:
                return {"success": True}
            else:
                error_msg = result.get("msg", "Unknown error")
                # Handle specific error codes
                code = result.get("code")
                if code == 1254290:  # TooManyRequest
                    error_msg = "请求过快，请稍后重试"
                elif code == 1254291:  # Write conflict
                    error_msg = "并发冲突，请稍后重试"
                return {"success": False, "error": error_msg, "code": code}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {e}"}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sync Amazon crawler data to Feishu Bitable",
        epilog="Example: python feishu_sync.py output/amazon_products.csv"
    )
    parser.add_argument(
        "csv_file",
        type=str,
        help="Path to CSV file to sync"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to config file"
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Simulate sync without actual API calls"
    )

    args = parser.parse_args()

    # Create sync client
    sync = FeishuSync(config_path=args.config)

    # Sync data
    result = sync.sync_csv(args.csv_file)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"\n=== 同步结果 ===")
    print(f"总计: {result['total']} 条")
    print(f"成功: {result['success']} 条")
    print(f"失败: {result['failed']} 条")


if __name__ == "__main__":
    main()
