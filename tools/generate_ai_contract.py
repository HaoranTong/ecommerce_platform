

'''
 脚本功能：合并
 - docs/design/modules/user-auth/frontend-rules.json
 - app/modules/user_auth/api.schema.json
    生成 AI 前端契约文件：app/modules/<code_module_name>/ai-frontend-contract.json
使用方法：
 从项目根目录运行： python tools/generate_ai_contract.py user-auth
'''

import json
from pathlib import Path
import sys
import re

def normalize_to_code_name(doc_module_name: str) -> str:
    """将文档中的连字符模块名（如 user-auth）转换为代码中的下划线名（user_auth）"""
    return doc_module_name.replace("-", "_")

def normalize_to_doc_name(code_module_name: str) -> str:
    """将代码中的下划线模块名（如 user_auth）转换为文档中的连字符名（user-auth）"""
    return code_module_name.replace("_", "-")

def generate_contract(doc_module_name: str):
    # 1. 路径映射
    doc_module_dir = Path("docs/design/modules") / doc_module_name
    code_module_name = normalize_to_code_name(doc_module_name)
    code_module_dir = Path("app/modules") / code_module_name

    # 2. 输入文件路径
    frontend_rules_path = doc_module_dir / "frontend-rules.json"
    api_schema_path = code_module_dir / "api.schema.json"

    # 3. 验证存在性
    if not doc_module_dir.exists():
        raise FileNotFoundError(f"❌ 设计文档模块目录不存在: {doc_module_dir}")
    if not code_module_dir.exists():
        raise FileNotFoundError(f"❌ 代码模块目录不存在: {code_module_dir}")
    if not frontend_rules_path.exists():
        raise FileNotFoundError(f"❌ 缺少 frontend-rules.json: {frontend_rules_path}")
    if not api_schema_path.exists():
        raise FileNotFoundError(f"❌ 缺少 api.schema.json: {api_schema_path}")

    # 4. 创建输出目录（在代码模块内）
    endpoints_dir = code_module_dir / "endpoints"
    models_dir = code_module_dir / "models"
    endpoints_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)

    # 5. 加载数据
    with open(frontend_rules_path, "r", encoding="utf-8") as f:
        frontend_rules = json.load(f)
    with open(api_schema_path, "r", encoding="utf-8") as f:
        api_schema = json.load(f)

    models = api_schema.get("definitions", {})

    # 6. 写入模型
    for model_name, schema in models.items():
        with open(models_dir / f"{model_name}.json", "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    # 7. 构建 endpoint 契约
    endpoint_contracts = {}
    for ep in frontend_rules["endpoints"]:
        name = ep["name"]
        request_type = ep.get("request", {})
        response_type = ep["response"]["type"]

        request_schema = {"type": "object", "properties": {}, "required": []}
        if isinstance(request_type, dict):
            for field, desc in request_type.items():
                is_optional = "optional" in desc.lower() or "?" in desc
                prop = {"type": "string", "description": desc}
                if not is_optional:
                    request_schema["required"].append(field)
                request_schema["properties"][field] = prop

        response_schema = {"type": "object"}
        if "[" in response_type and "]" in response_type:
            inner = response_type.split("[")[1].rstrip("]")
            if inner in models:
                response_schema = models[inner]
            elif inner.endswith("[]"):
                item_type = inner[:-2]
                response_schema = {
                    "type": "array",
                    "items": models.get(item_type, {"type": "object"})
                }

        errors = []
        for code, err in frontend_rules.get("error_codes", {}).items():
            errors.append({
                "code": code,
                "http_status": err["http_code"],
                "message": err["message"],
                "ui_hint": err.get("ui_hint", ""),
                "action": err.get("action", "")
            })

        contract = {
            "method": ep["method"],
            "path": ep["path"],
            "auth_required": ep.get("auth_required", False),
            "admin_only": ep.get("admin_only", False),
            "request_schema": request_schema,
            "response_schema": response_schema,
            "errors": errors,
            "notes": ep.get("notes", "")
        }

        endpoint_contracts[name] = contract
        with open(endpoints_dir / f"{name}.json", "w", encoding="utf-8") as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)

    # 8. 生成主契约文件
    ai_contract = {
        "module": frontend_rules["module"],
        "base_url": frontend_rules["base_path"],
        "auth": {"type": frontend_rules["auth_scheme"]},
        "token_schema": frontend_rules["token_schema"],
        "frontend_integration": frontend_rules["frontend_integration"],
        "security_notes": frontend_rules["security_notes"],
        "endpoints": endpoint_contracts
    }

    output_file = code_module_dir / "ai-frontend-contract.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ai_contract, f, indent=2, ensure_ascii=False)

    print(f"✅ AI 前端契约已生成！")
    print(f"   模块（文档）: {doc_module_name}")
    print(f"   模块（代码）: {code_module_name}")
    print(f"   输出位置    : {code_module_dir}")
    print(f"   主契约文件  : ai-frontend-contract.json")

def main():
    if len(sys.argv) != 2:
        print("用法: python tools/generate_ai_contract.py <doc-module-name>")
        print("说明: <doc-module-name> 是 docs/design/modules/ 下的目录名（使用连字符）")
        print("示例: python tools/generate_ai_contract.py user-auth")
        sys.exit(1)

    doc_module_name = sys.argv[1]
    generate_contract(doc_module_name)

if __name__ == "__main__":
    main()