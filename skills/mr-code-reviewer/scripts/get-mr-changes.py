#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.31.0",
#   "python-gitlab>=4.4.0",
# ]
# ///

"""
GitLab MR Changes Fetcher

获取 GitLab Merge Request 中变更文件的完整内容，用于代码审查。

用法:
    python get-mr-changes.py --url https://gitlab.com --project-id 12345 --mr-iid 42 --token glpat-xxx

    或使用环境变量:
    export GITLAB_URL=https://gitlab.com
    export GITLAB_TOKEN=glpat-xxx
    python get-mr-changes.py --project-id 12345 --mr-iid 42
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import gitlab
import requests


class MRChangesFetcher:
    """GitLab MR 变更获取器"""

    def __init__(
        self,
        gitlab_url: str,
        token: str,
        project_id: int,
        mr_iid: int,
        output_dir: Optional[Path] = None,
    ):
        """
        初始化 MR 变更获取器

        Args:
            gitlab_url: GitLab 实例 URL
            token: 访问令牌
            project_id: 项目 ID
            mr_iid: MR 的 IID (内部 ID)
            output_dir: 输出目录（可选）
        """
        self.gitlab_url = gitlab_url.rstrip("/")
        self.token = token
        self.project_id = project_id
        self.mr_iid = mr_iid
        self.output_dir = output_dir or Path("mr_changes")

        # 初始化 GitLab 客户端
        self.gl = gitlab.Gitlab(self.gitlab_url, private_token=self.token)
        self.project = self.gl.projects.get(self.project_id)
        self.mr = self.project.mergerequests.get(self.mr_iid)

    def get_mr_info(self) -> Dict:
        """获取 MR 基本信息"""
        return {
            "iid": self.mr.iid,
            "title": self.mr.title,
            "description": self.mr.description,
            "author": self.mr.author["name"],
            "source_branch": self.mr.source_branch,
            "target_branch": self.mr.target_branch,
            "state": self.mr.state,
            "web_url": self.mr.web_url,
            "created_at": self.mr.created_at,
            "updated_at": self.mr.updated_at,
        }

    def get_changed_files(self) -> List[Dict]:
        """
        获取 MR 中的变更文件列表

        Returns:
            包含文件信息的列表，每个文件包含：
            - old_path: 旧文件路径
            - new_path: 新文件路径
            - deleted_file: 是否被删除
            - new_file: 是否为新文件
            - renamed_file: 是否被重命名
        """
        changes = self.mr.changes()
        return changes.get("changes", [])

    def get_file_content(self, file_path: str, ref: str) -> Optional[str]:
        """
        获取指定文件的完整内容

        Args:
            file_path: 文件路径
            ref: Git 引用（分支名、commit SHA等）

        Returns:
            文件内容（字符串），如果文件不存在返回 None
        """
        try:
            file_obj = self.project.files.get(file_path=file_path, ref=ref)
            return file_obj.decode().decode("utf-8")
        except gitlab.exceptions.GitlabGetError:
            return None
        except UnicodeDecodeError:
            # 二进制文件
            return "[Binary file]"

    def fetch_all_changes(self) -> Dict:
        """
        获取 MR 的所有变更信息

        Returns:
            包含 MR 信息和文件内容的字典
        """
        print(f"Fetching MR #{self.mr_iid} from project {self.project_id}...")

        result = {
            "mr_info": self.get_mr_info(),
            "files": [],
        }

        changed_files = self.get_changed_files()
        print(f"Found {len(changed_files)} changed files")

        for idx, file_info in enumerate(changed_files, 1):
            old_path = file_info.get("old_path")
            new_path = file_info.get("new_path")
            deleted = file_info.get("deleted_file", False)
            new_file = file_info.get("new_file", False)
            renamed = file_info.get("renamed_file", False)

            print(f"  [{idx}/{len(changed_files)}] Processing: {new_path}")

            file_data = {
                "old_path": old_path,
                "new_path": new_path,
                "deleted": deleted,
                "new_file": new_file,
                "renamed": renamed,
                "old_content": None,
                "new_content": None,
            }

            # 获取旧文件内容（如果不是新文件）
            if not new_file and old_path:
                file_data["old_content"] = self.get_file_content(
                    old_path, self.mr.target_branch
                )

            # 获取新文件内容（如果没被删除）
            if not deleted and new_path:
                file_data["new_content"] = self.get_file_content(
                    new_path, self.mr.source_branch
                )

            result["files"].append(file_data)

        return result

    def save_to_json(self, data: Dict, filename: str = "mr_changes.json"):
        """将变更数据保存为 JSON 文件"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.output_dir / filename

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nSaved to: {output_file}")
        return output_file

    def save_individual_files(self, data: Dict):
        """将每个文件单独保存"""
        files_dir = self.output_dir / "files"
        files_dir.mkdir(parents=True, exist_ok=True)

        for file_info in data["files"]:
            new_path = file_info["new_path"]
            if not new_path or file_info["deleted"]:
                continue

            # 创建文件路径
            file_path = files_dir / new_path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存文件内容
            content = file_info["new_content"]
            if content and content != "[Binary file]":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

        print(f"Saved individual files to: {files_dir}")

    def generate_summary(self, data: Dict) -> str:
        """生成变更摘要"""
        mr_info = data["mr_info"]
        files = data["files"]

        # 统计文件类型
        file_types = {}
        for file_info in files:
            if file_info["deleted"]:
                continue
            path = file_info["new_path"]
            ext = Path(path).suffix or "[no extension]"
            file_types[ext] = file_types.get(ext, 0) + 1

        # 生成摘要
        summary = f"""# MR #{mr_info['iid']}: {mr_info['title']}

## 基本信息

- **作者**: {mr_info['author']}
- **源分支**: `{mr_info['source_branch']}`
- **目标分支**: `{mr_info['target_branch']}`
- **状态**: {mr_info['state']}
- **URL**: {mr_info['web_url']}

## 描述

{mr_info['description'] or '(无描述)'}

## 变更统计

- **总文件数**: {len(files)}
- **新增文件**: {sum(1 for f in files if f['new_file'])}
- **删除文件**: {sum(1 for f in files if f['deleted'])}
- **重命名文件**: {sum(1 for f in files if f['renamed'])}

## 文件类型分布

"""
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            summary += f"- `{ext}`: {count} 个文件\n"

        summary += "\n## 变更文件列表\n\n"
        for file_info in files:
            path = file_info["new_path"] or file_info["old_path"]
            status = []
            if file_info["new_file"]:
                status.append("新增")
            if file_info["deleted"]:
                status.append("删除")
            if file_info["renamed"]:
                status.append("重命名")
            if not status:
                status.append("修改")

            summary += f"- [{', '.join(status)}] `{path}`\n"

        return summary


def main():
    parser = argparse.ArgumentParser(
        description="获取 GitLab MR 的完整文件内容用于代码审查"
    )
    parser.add_argument(
        "--url",
        default=os.getenv("GITLAB_URL", "https://gitlab.com"),
        help="GitLab 实例 URL（默认: https://gitlab.com）",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITLAB_TOKEN"),
        help="GitLab 访问令牌（或设置 GITLAB_TOKEN 环境变量）",
    )
    parser.add_argument(
        "--project-id",
        type=int,
        required=True,
        help="项目 ID",
    )
    parser.add_argument(
        "--mr-iid",
        type=int,
        required=True,
        help="MR 的 IID（内部 ID）",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("mr_changes"),
        help="输出目录（默认: mr_changes）",
    )
    parser.add_argument(
        "--save-files",
        action="store_true",
        help="是否将文件单独保存到 files/ 子目录",
    )

    args = parser.parse_args()

    # 验证 token
    if not args.token:
        print("错误: 未提供 GitLab 访问令牌", file=sys.stderr)
        print("请使用 --token 参数或设置 GITLAB_TOKEN 环境变量", file=sys.stderr)
        sys.exit(1)

    try:
        # 创建获取器
        fetcher = MRChangesFetcher(
            gitlab_url=args.url,
            token=args.token,
            project_id=args.project_id,
            mr_iid=args.mr_iid,
            output_dir=args.output_dir,
        )

        # 获取变更数据
        data = fetcher.fetch_all_changes()

        # 保存 JSON
        fetcher.save_to_json(data)

        # 生成并保存摘要
        summary = fetcher.generate_summary(data)
        summary_file = args.output_dir / "SUMMARY.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Saved summary to: {summary_file}")

        # 可选：保存单独文件
        if args.save_files:
            fetcher.save_individual_files(data)

        print("\n✅ 完成！")

    except gitlab.exceptions.GitlabAuthenticationError:
        print("错误: GitLab 认证失败，请检查访问令牌", file=sys.stderr)
        sys.exit(1)
    except gitlab.exceptions.GitlabGetError as e:
        print(f"错误: 无法获取资源 - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
