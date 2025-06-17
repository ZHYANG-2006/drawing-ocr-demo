import time
import re
from celery import shared_task
import json
import os
import fitz
import requests
import base64
import numpy as np
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer
from sma.system.models.mco import MCOCMPPair, MCOCMPDiff, MCOPdfFile
from typing import List, Dict
from html import escape


# 1. 加载模型
model_name = "all-MiniLM-L6-v2"
# model_name = "/app/all-MiniLM-L6-v2"
# model_name = "D://QCPCPP//models//all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)
LLM_API_URL = "http://172.16.94.134:3003/v1/chat/completions"
# LLM_API_URL = "http://127.0.0.1:3003/v1/chat/completions"
LLM_MODEL_NAME = "deepseek-llm-7b-chat"

_WRAP_PATTERN = re.compile(r"\[.*?]|\{.*?}|<.*?>|>.*?<")

_punct = r'()[\]{}<>,.;:!?+*/\\\-="\'‒–—…§'
_strip_space_around_punct = re.compile(rf'\s*([{_punct}])\s*')
CONTEXT = 1
SIM_THRESHOLD = 0.75          # 语义阈值
PREFIX_LEN    = 180            # 最多比对新段前 N 个字符，避免超长字符串

def normalize(text: str) -> str:
    def repl(m: re.Match) -> str:
        ch   = m.group(1)
        prev = m.string[m.start() - 1] if m.start() > 0 else ''
        nxt  = m.string[m.end()]       if m.end()   < len(m.string) else ''
        # “数字 . 数字” 或 “数字 - 数字” 时保留原样
        if ch in '.-' and prev.isdigit() and nxt.isdigit():
            return ch
        return f' {ch} '
    return _strip_space_around_punct.sub(repl, text).strip()

_token_pattern = re.compile(
    r'\d+(?:[.-]\d+)+|'   # ⬅️ 小数 & 连字符序列号
    r'\w+(?:-\w+)*|'      # 单词 / foo-bar
    r'[^\w\s]'            # 单个标点
)

def tokenize(text: str):
    return _token_pattern.findall(normalize(text))

# # ② 基于正则的 tokenizer：单词 / 数字 / 连字符 / 单个标点
# _token_pattern = re.compile(r'\w+(?:-\w+)*|[^\w\s]')
#
# def tokenize(text: str) -> List[str]:
#     text = normalize(text)
#     return _token_pattern.findall(text)

def get_paragraph_image_base64(pdf_path, polygon, page_index=0):
    """
    从 pdf_path 对应的 PDF 中，截取 page_index 页上 polygon 范围内的图像，并返回 Base64 编码字符串。
    polygon 假设为 [x1, y1, x2, y2, x3, y3, x4, y4]，(x1, y1) 是左上角，(x3, y3) 是右下角。
    如果段落信息带有实际的 page_num，你可以用 doc.load_page(page_num-1)。
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_index)

    # 简单处理坐标，取左上角和右下角
    [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] = polygon
    left = min(x1, x3)
    top = min(y1, y3)
    right = max(x1, x3)
    bottom = max(y1, y3)
    rect = fitz.Rect(left, top, right, bottom)

    # 截图
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), clip=rect)

    # 转 PNG 字节流
    png_bytes = pix.tobytes("png")
    # Base64 编码
    base64_data = base64.b64encode(png_bytes).decode('utf-8')

    doc.close()
    # 加上前缀，方便前端 <img> 直接使用
    return f"data:image/png;base64,{base64_data}"

def get_word_level_diff(old_text: str, new_text: str) -> List[Dict[str, str]]:
    old_tokens = tokenize(old_text)
    new_tokens = tokenize(new_text)

    matcher = SequenceMatcher(None, old_tokens, new_tokens)
    diff_result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue

        # 片段本身
        old_seg = " ".join(old_tokens[i1:i2])
        new_seg = " ".join(new_tokens[j1:j2])

        # 左右上下文
        old_left  = " ".join(old_tokens[max(0, i1-CONTEXT):i1])
        old_right = " ".join(old_tokens[i2:i2+CONTEXT])
        new_left  = " ".join(new_tokens[max(0, j1-CONTEXT):j1])
        new_right = " ".join(new_tokens[j2:j2+CONTEXT])
        old_seg = re.sub(' - ', '-', old_seg)
        old_seg = re.sub(' -', '-', old_seg)
        old_seg = re.sub('- ', '-', old_seg)
        old_seg = re.sub(' \.', '.', old_seg)
        old_seg = re.sub('\+ /-', '+/- ', old_seg)
        old_seg = re.sub(' :', ':', old_seg)
        old_seg = re.sub(' MM', 'MM', old_seg)
        old_seg = re.sub(' ,', ',', old_seg)
        new_seg = re.sub(' - ', '-', new_seg)
        new_seg = re.sub(' -', '-', new_seg)
        new_seg = re.sub('- ', '-', new_seg)
        new_seg = re.sub(' \.', '.', new_seg)
        new_seg = re.sub('\+ /-', '+/- ', new_seg)
        new_seg = re.sub(' :', ':', new_seg)
        new_seg = re.sub(' MM', 'MM', new_seg)
        new_seg = re.sub(' ,', ',', new_seg)
        old_left = re.sub(' - ', '-', old_left)
        old_left = re.sub(' -', '-', old_left)
        old_left = re.sub('- ', '-', old_left)
        old_left = re.sub(' \.', '.', old_left)
        old_left = re.sub('\+ /-', '+/- ', old_left)
        old_left = re.sub(' :', ':', old_left)
        old_left = re.sub(' MM', 'MM', old_left)
        old_left = re.sub(' ,', ',', old_left)
        old_right = re.sub(' - ', '-', old_right)
        old_right = re.sub(' -', '-', old_right)
        old_right = re.sub('- ', '-', old_right)
        old_right = re.sub(' \.', '.', old_right)
        old_right = re.sub('\+ /-', '+/- ', old_right)
        old_right = re.sub(' :', ':', old_right)
        old_right = re.sub(' MM', 'MM', old_right)
        old_right = re.sub(' ,', ',', old_right)
        new_left = re.sub(' - ', '-', new_left)
        new_left = re.sub(' -', '-', new_left)
        new_left = re.sub('- ', '-', new_left)
        new_left = re.sub(' \.', '.', new_left)
        new_left = re.sub('\+ /-', '+/- ', new_left)
        new_left = re.sub(' :', ':', new_left)
        new_left = re.sub(' MM', 'MM', new_left)
        new_left = re.sub(' ,', ',', new_left)
        new_right = re.sub(' - ', '-', new_right)
        new_right = re.sub(' -', '-', new_right)
        new_right = re.sub('- ', '-', new_right)
        new_right = re.sub(' \.', '.', new_right)
        new_right = re.sub('\+ /-', '+/- ', new_right)
        new_right = re.sub(' :', ':', new_right)
        new_right = re.sub(' MM', 'MM', new_right)
        new_right = re.sub(' ,', ',', new_right)
        diff_item = {
            "type": tag,            # insert / delete / replace
            "old_text": old_seg,
            "new_text": new_seg,
            "old_left": old_left,
            "old_right": old_right,
            "new_left": new_left,
            "new_right": new_right,
        }
        diff_result.append(diff_item)

    return diff_result

def clean_value(text: str) -> str:
    """
    去除包裹符号内的内容并截取到首个 '.' 之前
    """
    if not text:
        return text
    cleaned = _WRAP_PATTERN.sub("", text).strip()
    dot_idx = cleaned.find(".")
    if dot_idx != -1:
        cleaned = cleaned[dot_idx + 1:]
    return cleaned.strip()

WHITE = r'(?:\s|\u00A0)'

def _re_escape(s: str | None) -> str:
    return re.escape(s or "")

def _looseify(segment: str | None) -> str:
    if not segment:
        return ""

    # 1) 先把多余空白折叠，避免生成多余的 '\ ' 转义
    segment = re.sub(r'\s+', ' ', segment.strip())

    # 2) 整体转义
    pattern = re.escape(segment)

    # 3) 把转义空格替换成“可选空白”
    pattern = pattern.replace(r'\ ', f'{WHITE}*')

    # 4) 如果还想把原文里的 \s+ 也放宽，用 lambda 避免替换串被再次解释
    pattern = re.sub(r'\\s\+', lambda _: f'{WHITE}*', pattern)

    return pattern
def _flex_mid(m: str) -> str:
    escaped = re.escape(m)
    return re.sub(r'\\\s+', r'\\s*', escaped)

# ③ 构造窗口正则：left (center) right
def build_window_regex(left: str | None,
                       mid: str | None,
                       right: str | None) -> re.Pattern:
    l = f"{_looseify(left)}{WHITE}*" if left else ""
    r = f"{WHITE}*{_looseify(right)}" if right else ""
    c = f"({_looseify(mid)})"         # 捕获中心词
    return re.compile(f"{l}{c}{r}", flags=re.S | re.I)  # dotAll + 忽略大小写

def _wrap_once(m, cls):
    start, end = m.span(1)         # 捕获组在整个 match 内的偏移
    inner = escape(m.group(1))
    return (
        m.group(0)[: start - m.start(0)] +
        f'<span class="{cls}">{inner}</span>' +
        m.group(0)[end - m.start(0):]
    )

def highlight_text(text: str, diffs: list[dict], mode: str, cmptype: str) -> str:
    if not diffs:
        if cmptype == "deleted":
            return f'<span class="diff-delete">{escape(text)}</span>'
        elif cmptype == "inserted":
            return f'<span class="diff-insert">{escape(text)}</span>'
        else:
            return escape(text)
    html = text + " "
    for d in diffs:
        d_type = d.get("type")
        # reg = build_window_regex(d['new_left'], d['new_text'], d['new_right'])
        # hit = reg.search(html)
        # print(d['new_text'][:40], '->', bool(hit))
        # if not hit:
        #     print('pattern:', reg.pattern)  # 把生成的正则打印出来
        #     print('附近原文:', html[html.find(d['new_left']) - 20:
        #                             html.find(d['new_left']) + 120])
        #     break

        # 旧段落：delete / replace
        if mode == "old" and d_type in {"delete", "replace"} and (d.get("old_text") or "").strip():
            reg = build_window_regex(d.get("old_left"), d["old_text"], d.get("old_right"))
            cls = "diff-delete" if d_type == "delete" else "diff-replace-old"
            html = reg.sub(lambda m: _wrap_once(m, cls), html)

        # 新段落：insert / replace
        if mode == "new" and d_type in {"insert", "replace"} and (d.get("new_text") or "").strip():
            reg = build_window_regex(d.get("new_left"), d["new_text"], d.get("new_right"))
            cls = "diff-insert" if d_type == "insert" else "diff-replace-new"
            html = reg.sub(lambda m: _wrap_once(m, cls), html)

    return html

def _normalize(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip().lower()

def _normalize_ws(s: str) -> str:
    return s.replace('\u00A0', ' ')

def compare_pdf(old_paragraphs, new_paragraphs, old_file_id, new_file_id, output_json="diff_output.json"):
    old_pdf = MCOPdfFile.objects.get(pk=old_file_id)
    new_pdf = MCOPdfFile.objects.get(pk=new_file_id)
    cmp_pair = MCOCMPPair.objects.create(
        old_pdf=old_pdf,
        new_pdf=new_pdf,
    )
    old_file_path = old_pdf.file_path
    new_file_path = new_pdf.file_path
    # 1. 提取文本列表
    old_texts = [p["value"] for p in old_paragraphs]
    new_texts = [p["value"] for p in new_paragraphs]

    # 2. 段落语义向量
    old_emb = model.encode(old_texts, convert_to_numpy=True, normalize_embeddings=True)
    new_emb = model.encode(new_texts, convert_to_numpy=True, normalize_embeddings=True)

    # 3. 相似度矩阵
    sim_matrix = np.inner(old_emb, new_emb)

    old2new_match = {}
    new_matched = set()

    # ---------- 1) 语义阈值匹配 ----------
    for i in range(sim_matrix.shape[0]):
        j_best = int(np.argmax(sim_matrix[i]))
        best_sim = sim_matrix[i, j_best]

        if best_sim >= SIM_THRESHOLD and j_best not in new_matched:
            old2new_match[i] = j_best
            new_matched.add(j_best)

    # ---------- 2) 段首包含兜底 ----------
    for i, old_p in enumerate(old_paragraphs):
        if i in old2new_match:  # 已匹配跳过
            continue
        norm_old = _normalize(old_p["value"])

        for j, new_p in enumerate(new_paragraphs):
            if j in new_matched:
                continue
            norm_new_prefix = _normalize(new_p["value"][:PREFIX_LEN])

            # 判断条件：旧段文本是新段“前缀”或相似度≥0.9（防空格差异）
            if norm_new_prefix.startswith(norm_old) or \
                    SequenceMatcher(None, norm_old, norm_new_prefix).ratio() >= 0.9:
                old2new_match[i] = j
                new_matched.add(j)
                break  # 一旦成功就退出内层循环
    # 用于最终输出的两个列表
    sdiff = []
    ldiff = []

    # 5. 处理匹配到的段落：sdiff
    for old_idx, new_idx in old2new_match.items():
        old_para = old_paragraphs[old_idx]
        new_para = new_paragraphs[new_idx]

        old_val = old_para["value"]
        new_val = new_para["value"]
        old_val = clean_value(old_val)
        new_val = clean_value(new_val)

        old_num = old_para["num"]
        new_num = new_para["num"]
        if old_val.strip() == new_val.strip():
            continue
        old_polygon = old_para["polygon"]
        new_polygon = new_para["polygon"]
        # added_system_prompt = (
        #     "你是“段落差异提取器”。"
        #     "【任务】只列出新旧段落之间的差异点，每行一个 bullet。"
        #     "【禁止】不要出现“问题：”“回答：”“主要区别”之类说明，也不要复述整段原文。"
        #     "【格式】输出示例：\n"
        #     "- 将 panel tabs 最大厚度从 0.10 mm 调整为 0.15 mm\n"
        #     "- 删除了 XXX 要求\n"
        #     "- 新增了 YYY 条件\n"
        # )
        added_system_prompt = (
            "你是“段落差异提取器”。"
            "【任务】只列出新旧段落之间的差异点，每行一个 bullet。"
            "【禁止】不要出现“问题：”“回答：”之类说明，也不要复述整段原文。"
            "【格式】主要区别："
        )
        prompt = (
            f"旧版本段落：\n{old_val}\n\n"
            f"新版本段落：\n{new_val}"
        )

        # 截图 -> Base64
        old_pic_base64 = get_paragraph_image_base64(old_file_path, old_polygon, page_index=0)
        new_pic_base64 = get_paragraph_image_base64(new_file_path, new_polygon, page_index=0)

        payload = {
            "model": LLM_MODEL_NAME,
            "messages": [
                {"role": "system", "content": added_system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2048
        }
        analyze = ""
        # try:
        #     resp = requests.post(LLM_API_URL, json=payload, timeout=600)
        #     resp.raise_for_status()
        #     data = resp.json()
        #     if "choices" in data and len(data["choices"]) > 0:
        #         analyze = data["choices"][0]["message"]["content"].strip()
        #     else:
        #         analyze = "(No difference analysis returned.)"
        # except Exception as e:
        #     analyze = f"(Error calling LLM ChatCompletion: {e})"
        diff = get_word_level_diff(old_val, new_val)
        if diff is None or diff == "" or len(diff) == 0:
            continue
        old_val = re.sub(' - ', '-', old_val)
        old_val = re.sub(' -', '-', old_val)
        old_val = re.sub('- ', '-', old_val)
        old_val = re.sub(' \.', '.', old_val)
        old_val = re.sub('\+ /-', '+/- ', old_val)
        old_val = re.sub(' :', ':', old_val)
        old_val = re.sub(' MM', 'MM', old_val)
        new_val = re.sub(' - ', '-', new_val)
        new_val = re.sub(' -', '-', new_val)
        new_val = re.sub('- ', '-', new_val)
        new_val = re.sub(' \.', '.', new_val)
        new_val = re.sub('\+ /-', '+/- ', new_val)
        new_val = re.sub(' :', ':', new_val)
        new_val = re.sub(' MM', 'MM', new_val)
        sdiff.append({
            "old_para_value": old_val + ' ',
            "new_para_value": new_val + ' ',
            "old_para_polygon": old_polygon,
            "new_para_polygon": new_polygon,
            "old_para_pic": old_pic_base64,  # 这里直接放 Base64
            "new_para_pic": new_pic_base64,
            "analyze": analyze,
            "diff": diff
        })
        cmp_diff = MCOCMPDiff.objects.create(
            cmp_pair=cmp_pair,
            old_pdf_path=old_file_path,
            new_pdf_path=new_file_path,
            old_para_polygon=old_polygon,
            new_para_polygon=new_polygon,
            old_para_value=old_val,
            new_para_value=new_val,
            old_para_num=old_num,
            new_para_num=new_num,
            type='diff',
            analyze=analyze,
            diff=diff,
        )

    # 6. 未匹配的：ldiff
    # (a) 旧文档被删除
    unmatched_old = [i for i in range(len(old_paragraphs)) if i not in old2new_match]
    for i in unmatched_old:
        old_para = old_paragraphs[i]
        old_val = old_para["value"]
        old_num = old_para["num"]
        old_polygon = old_para["polygon"]
        old_pic_base64 = get_paragraph_image_base64(old_file_path, old_polygon, page_index=0)

        ldiff.append({
            "type": "deleted",
            "para_value": old_val,
            "para_polygon": old_polygon,
            "para_pic": old_pic_base64
        })
        cmp_diff = MCOCMPDiff.objects.create(
            cmp_pair=cmp_pair,
            old_pdf_path=old_file_path,
            new_pdf_path=new_file_path,
            old_para_polygon=old_polygon,
            old_para_value=old_val,
            old_para_num=old_num,
            type='deleted',
            analyze='该段落在新版本中被删除',
        )

    # (b) 新文档新增
    unmatched_new = [j for j in range(len(new_paragraphs)) if j not in new_matched]
    for j in unmatched_new:
        new_para = new_paragraphs[j]
        new_val = new_para["value"]
        new_num = new_para["num"]
        new_polygon = new_para["polygon"]
        new_pic_base64 = get_paragraph_image_base64(new_file_path, new_polygon, page_index=0)

        ldiff.append({
            "type": "inserted",
            "para_value": new_val,
            "para_polygon": new_polygon,
            "para_pic": new_pic_base64
        })

        cmp_diff = MCOCMPDiff.objects.create(
            cmp_pair=cmp_pair,
            old_pdf_path=old_file_path,
            new_pdf_path=new_file_path,
            new_para_polygon=new_polygon,
            new_para_value=new_val,
            new_para_num=new_num,
            type='inserted',
            analyze='该段落为新版本新增内容。',
        )
    cmp_diffs = MCOCMPDiff.objects.filter(cmp_pair=cmp_pair)
    html_old_str = ''
    html_new_str = ''
    for para in old_paragraphs:
        html_str = para["value"]
        html_str = re.sub(' - ', '-', html_str)
        html_str = re.sub(' -', '-', html_str)
        html_str = re.sub('- ', '-', html_str)
        html_str = re.sub(' \.', '.', html_str)
        html_str = re.sub('\+ /-', '+/- ', html_str)
        html_str = re.sub(' :', ':', html_str)
        html_str = re.sub(' MM', 'MM', html_str)
        for cmp in cmp_diffs:
            if cmp.old_para_num == para["num"]:
                html_str = highlight_text(html_str, cmp.diff, "old", cmp.type)
        html_old_str = html_old_str + html_str + '<br/>'
    for para in new_paragraphs:
        html_str = para["value"]
        html_str = re.sub(' - ', '-', html_str)
        html_str = re.sub(' -', '-', html_str)
        html_str = re.sub('- ', '-', html_str)
        html_str = re.sub(' \.', '.', html_str)
        html_str = re.sub('\+ /-', '+/- ', html_str)
        html_str = re.sub(' :', ':', html_str)
        html_str = re.sub(' MM', 'MM', html_str)
        for cmp in cmp_diffs:
            if cmp.new_para_num == para["num"]:
                html_str = highlight_text(html_str, cmp.diff, "new", cmp.type)
        html_new_str = html_new_str + html_str + '<br/>'
    html_old_str = re.sub(' - ', '-', html_old_str)
    html_old_str = re.sub(' -', '-', html_old_str)
    html_old_str = re.sub('- ', '-', html_old_str)
    html_old_str = re.sub(' \.', '.', html_old_str)
    html_old_str = re.sub('\+ /-', '+/- ', html_old_str)
    html_old_str = re.sub(' :', ':', html_old_str)
    html_old_str = re.sub(' MM', 'MM', html_old_str)
    html_new_str = re.sub(' - ', '-', html_new_str)
    html_new_str = re.sub(' -', '-', html_new_str)
    html_new_str = re.sub('- ', '-', html_new_str)
    html_new_str = re.sub(' \.', '.', html_new_str)
    html_new_str = re.sub('\+ /-', '+/- ', html_new_str)
    html_new_str = re.sub(' :', ':', html_new_str)
    html_new_str = re.sub(' MM', 'MM', html_new_str)
    # 在真正高亮之前：
    html_old_str = _normalize_ws(html_old_str)
    html_new_str = _normalize_ws(html_new_str)
    article = {
        "old_article": html_old_str,
        "new_article": html_new_str,
    }
    # 7. 组装JSON
    result_dict = {
        "article": article,
        "sdiff": sdiff,
        "ldiff": ldiff
    }

    # 保存到文件
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)

    # 同时打印到控制台
    # print(json.dumps(result_dict, ensure_ascii=False, indent=2))
    return result_dict

if __name__ == "__main__":
    old_file_path = "D:/home/student4/ocrtest/data/input/sample4.pdf"
    new_file_path = "D:/home/student4/ocrtest/data/input/sample5.pdf"

    old_paragraphs = [
        {"num": 1, "value": "PULL FORCE MUST BE GREATER THAN 5 N.",
         "polygon": [12,25,210,25,210,125,12,125]},
        {"num": 2, "value": "INSPECT AND MEASURE AFTER BENDING AT FATP BEFORE SYSTEM ASSEMBLY.",
         "polygon": [15,130,200,130,200,180,15,180]},
        {"num": 3, "value": "THIS PARAGRAPH WAS DELETED IN THE NEW VERSION",
         "polygon": [12,190,210,190,210,250,12,250]},
        {"num": 4, "value": "THIS xcscsdc DELETED IN asdadadasd abc",
         "polygon": [12, 190, 210, 190, 210, 250, 12, 250]}
    ]

    new_paragraphs = [
        {"num": 1, "value": "PULL FORCE MUST BE GREATER THAN 1 N.",
         "polygon": [12,25,210,25,210,125,12,125]},
        {"num": 2, "value": "THIS PARAGRAPH IS NEWLY ADDED.",
         "polygon": [15,130,200,130,200,180,15,180]},
        {"num": 3, "value": "THIS xcscsdc DELETED IN asdadadasd",
         "polygon": [12, 190, 210, 190, 210, 250, 12, 250]}
    ]

    compare_pdf(old_paragraphs, new_paragraphs, old_file_path, new_file_path, output_json="base64_diff_output.json")

@shared_task(bind=True)
def compare_pdfs_task(self, old_file_id, new_file_id, old_paragraphs, new_paragraphs):
    """
    后台异步执行的任务，用于对比 old_file_path / new_file_path 两个pdf的段落。
    这里示范把结果直接存成一个json文件，也可存数据库/redis等。
    """
    result = compare_pdf(old_paragraphs, new_paragraphs, old_file_id, new_file_id, output_json="diff_output.json")

    return {"status": "done", "result": result}


# @shared_task
# def add(a, b):
#     return a + b
