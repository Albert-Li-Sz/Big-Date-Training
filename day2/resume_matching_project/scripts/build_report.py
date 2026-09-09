"""生成课程项目报告 DOCX。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "基于大数据与AI的简历岗位人才匹配系统项目报告.docx"
SCREENSHOTS = ROOT / "docs" / "screenshots"
RESULTS = ROOT / "output" / "full_matches.csv"

NAVY = "102A56"
BLUE = "2457E6"
PALE_BLUE = "EEF3FF"
PALE_GRAY = "F4F6FA"
MID_GRAY = "66748A"
LINE = "D9E1EC"
TEAL = "0B8D79"
AMBER = "C57910"
WHITE = "FFFFFF"
# 使用 macOS 系统自带、对无用户主目录的 headless LibreOffice 也可见的
# CJK 字体，保证本地渲染与最终交付中的中文不会退化为方框。
FONT_CN = "Arial Unicode MS"
FONT_LATIN = "Arial Unicode MS"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_border(cell, color: str = LINE, width: str = "6") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = qn(f"w:{edge}")
        element = borders.find(tag)
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), width)
        element.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    table_header = OxmlElement("w:tblHeader")
    table_header.set(qn("w:val"), "true")
    tr_pr.append(table_header)


def set_run_font(run, size: float | None = None, bold: bool | None = None, color: str | None = None) -> None:
    run.font.name = FONT_LATIN
    fonts = run._element.get_or_add_rPr().rFonts
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{attribute}"), FONT_CN)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def style_paragraph(paragraph, size: float = 10.5, color: str = NAVY, spacing: float = 6) -> None:
    paragraph.paragraph_format.space_after = Pt(spacing)
    paragraph.paragraph_format.line_spacing = 1.35
    for run in paragraph.runs:
        set_run_font(run, size=size, color=color)


def add_text(document: Document, text: str, bold_prefix: str | None = None) -> None:
    paragraph = document.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):
        prefix = paragraph.add_run(bold_prefix)
        set_run_font(prefix, size=10.5, bold=True, color=NAVY)
        body = paragraph.add_run(text[len(bold_prefix) :])
        set_run_font(body, size=10.5, color=NAVY)
    else:
        run = paragraph.add_run(text)
        set_run_font(run, size=10.5, color=NAVY)
    paragraph.paragraph_format.space_after = Pt(7)
    paragraph.paragraph_format.line_spacing = 1.35


def add_bullets(document: Document, items: list[str]) -> None:
    for item in items:
        paragraph = document.add_paragraph(style="List Bullet")
        run = paragraph.add_run(item)
        set_run_font(run, size=10.2, color=NAVY)
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.25


def add_numbered(document: Document, items: list[str]) -> None:
    for item in items:
        paragraph = document.add_paragraph(style="List Number")
        run = paragraph.add_run(item)
        set_run_font(run, size=10.2, color=NAVY)
        paragraph.paragraph_format.space_after = Pt(4)


def add_heading(document: Document, text: str, level: int = 1) -> None:
    paragraph = document.add_heading(text, level=level)
    color = NAVY if level == 1 else BLUE
    size = 18 if level == 1 else 13
    paragraph.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    paragraph.paragraph_format.space_after = Pt(8)
    for run in paragraph.runs:
        set_run_font(run, size=size, bold=True, color=color)


def add_table(document: Document, headers: list[str], rows: list[list[object]], widths: list[float] | None = None):
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table.autofit = False
    set_repeat_table_header(table.rows[0])
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = str(header)
        set_cell_shading(cell, NAVY)
        set_cell_border(cell, WHITE)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in paragraph.runs:
            set_run_font(run, size=8.8, bold=True, color=WHITE)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for column_index, value in enumerate(row):
            cell = cells[column_index]
            cell.text = str(value)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_shading(cell, WHITE if row_index % 2 == 0 else PALE_GRAY)
            set_cell_border(cell)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.05
                for run in paragraph.runs:
                    set_run_font(run, size=8.2, color=NAVY)
    if widths:
        for row in table.rows:
            for cell, width in zip(row.cells, widths):
                cell.width = Inches(width)
    document.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_code_block(document: Document, lines: list[str]) -> None:
    table = document.add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    set_cell_shading(cell, "0B1F3A")
    set_cell_border(cell, "0B1F3A")
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    for index, line in enumerate(lines):
        run = paragraph.add_run(line + ("\n" if index < len(lines) - 1 else ""))
        run.font.name = FONT_CN
        fonts = run._element.get_or_add_rPr().rFonts
        for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
            fonts.set(qn(f"w:{attribute}"), FONT_CN)
        run.font.size = Pt(8.2)
        run.font.color.rgb = RGBColor.from_string("E8EEF8")
    document.add_paragraph().paragraph_format.space_after = Pt(0)


def add_picture(document: Document, filename: str, caption: str, width: float = 6.45) -> None:
    path = SCREENSHOTS / filename
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    run.add_picture(str(path), width=Inches(width))
    caption_paragraph = document.add_paragraph()
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_run = caption_paragraph.add_run(caption)
    set_run_font(caption_run, size=8.5, color=MID_GRAY)
    caption_paragraph.paragraph_format.space_after = Pt(7)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("第 ")
    set_run_font(run, size=8, color=MID_GRAY)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, end])
    tail = paragraph.add_run(" 页")
    set_run_font(tail, size=8, color=MID_GRAY)


def configure_document(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Cm(1.9)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.header_distance = Cm(0.8)
    section.footer_distance = Cm(0.8)

    normal = document.styles["Normal"]
    normal.font.name = FONT_LATIN
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        normal._element.rPr.rFonts.set(qn(f"w:{attribute}"), FONT_CN)
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(NAVY)

    for style_name in ["Title", "Subtitle", "Heading 1", "Heading 2", "List Bullet", "List Number"]:
        style = document.styles[style_name]
        style.font.name = FONT_LATIN
        for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
            style._element.rPr.rFonts.set(qn(f"w:{attribute}"), FONT_CN)

    header = section.header
    header_table = header.add_table(rows=1, cols=2, width=Inches(6.45))
    header_table.columns[0].width = Inches(5.2)
    header_table.columns[1].width = Inches(1.25)
    left = header_table.cell(0, 0)
    right = header_table.cell(0, 1)
    left.text = "简历岗位人才匹配系统"
    right.text = "项目报告"
    right.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for cell in (left, right):
        set_cell_shading(cell, WHITE)
        set_cell_border(cell, WHITE, "0")
        for run in cell.paragraphs[0].runs:
            set_run_font(run, size=8, bold=True, color=BLUE)
    footer = section.footer
    footer_paragraph = footer.paragraphs[0]
    footer_paragraph.add_run("课程项目交付文件")
    set_run_font(footer_paragraph.runs[0], size=8, color=MID_GRAY)
    add_page_number(footer.add_paragraph())


def add_cover(document: Document) -> None:
    spacer = document.add_paragraph()
    spacer.paragraph_format.space_after = Pt(55)
    eyebrow = document.add_paragraph()
    eyebrow.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = eyebrow.add_run("大数据与人工智能课程项目")
    set_run_font(run, size=11, bold=True, color=BLUE)
    eyebrow.paragraph_format.space_after = Pt(18)

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("基于大数据与人工智能的\n简历岗位人才匹配系统")
    set_run_font(title_run, size=26, bold=True, color=NAVY)
    title.paragraph_format.line_spacing = 1.15
    title.paragraph_format.space_after = Pt(22)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle.add_run("设计说明  算法实现  大数据链路  系统验证")
    set_run_font(subtitle_run, size=12, color=MID_GRAY)
    subtitle.paragraph_format.space_after = Pt(42)

    summary = document.add_table(rows=4, cols=2)
    summary.alignment = WD_ALIGN_PARAGRAPH.CENTER
    labels = ["实现范围", "运行环境", "数据规模", "完成日期"]
    values = [
        "文本预处理、双语义模型、七维评分、双向推荐、可视化",
        "Ubuntu 24.04、Hadoop 3.3.6、Spark 3.5.1、Python 3.12",
        "12 份简历、12 个岗位、144 组全量配对",
        "2026 年 9 月",
    ]
    for row_index, (label, value) in enumerate(zip(labels, values)):
        label_cell, value_cell = summary.rows[row_index].cells
        label_cell.text = label
        value_cell.text = value
        set_cell_shading(label_cell, PALE_BLUE)
        set_cell_shading(value_cell, WHITE)
        for cell in (label_cell, value_cell):
            set_cell_border(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in label_cell.paragraphs[0].runs:
            set_run_font(run, size=9.5, bold=True, color=BLUE)
        for run in value_cell.paragraphs[0].runs:
            set_run_font(run, size=9.5, color=NAVY)
    note = document.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note_run = note.add_run("本地 Docker 实测版")
    set_run_font(note_run, size=10, bold=True, color=TEAL)
    note.paragraph_format.space_before = Pt(34)
    document.add_page_break()


def build_report() -> Document:
    if not RESULTS.exists():
        raise FileNotFoundError("缺少 output/full_matches.csv，请先运行匹配器")
    full = pd.read_csv(RESULTS, encoding="utf-8-sig")
    top = full.loc[full["resume_rank"] == 1].sort_values("resume_id")
    document = Document()
    configure_document(document)
    document.core_properties.title = "基于大数据与人工智能的简历岗位人才匹配系统项目报告"
    document.core_properties.subject = "课程项目设计与本地运行验证"
    document.core_properties.author = "课程项目组"
    add_cover(document)

    add_heading(document, "摘要")
    add_text(
        document,
        "本项目实现了一套可在课程 Docker 镜像中独立运行的简历岗位人才匹配系统。系统读取结构化 CSV，使用 jieba 分词、停用词过滤和技能别名归一完成预处理；再分别计算 TF-IDF 与 Word2Vec 余弦相似度，并与技能覆盖、学历、经验、城市和证书规则合成为七维总分。系统同时输出学生找岗位和岗位找人才两种 Top N 排名，并为每组结果给出命中技能、缺失技能和规则判断。",
    )
    add_text(
        document,
        f"实测数据包含 12 份简历和 12 个岗位，共生成 {len(full)} 组配对。每名学生的 Top 1 平均分为 {top['total_score'].mean():.2f}，最高分为 {top['total_score'].max():.2f}，最低分为 {top['total_score'].min():.2f}。HDFS、PySpark 清洗、MLlib Word2Vec、Streamlit 和 CSV 导出均在本地镜像中完成验证。",
    )
    add_text(document, "关键词：Hadoop；Spark；jieba；TF-IDF；Word2Vec；余弦相似度；Streamlit；人岗匹配")

    add_heading(document, "项目结论", level=2)
    add_bullets(
        document,
        [
            "系统覆盖任务书的最低功能，并实现双向推荐、证书和薪资诊断、CSV 上传筛选、MLlib Word2Vec 与自动化测试。",
            "TF-IDF 保留关键词重合的可解释性，Word2Vec 补充语义邻近，规则评分控制硬性条件；三类证据共同决定排序。",
            "示例数据的 12 个 Top 1 均满足学历、经验和城市要求，说明权重在当前教学数据上能够优先返回方向一致的岗位。",
        ],
    )
    document.add_page_break()

    add_heading(document, "一 项目目标与需求落实")
    add_text(
        document,
        "系统服务高校学生和招聘岗位两个视角。学生需要知道哪些岗位更匹配以及需要补充哪些技能；招聘方需要从多名学生中获得有依据的候选人排序。实现以任务书为功能基线，并把每项要求落到可运行文件和验证证据。",
    )
    checklist = [
        ["CSV 数据", "resumes.csv 与 jobs.csv", "已完成"],
        ["文本预处理", "jieba、停用词、别名标准化", "已完成"],
        ["语义计算", "TF-IDF 与 gensim Word2Vec", "已完成"],
        ["规则评分", "技能、学历、经验、城市、证书、薪资", "已完成"],
        ["Top N 推荐", "学生视角与岗位视角", "已完成"],
        ["推荐解释", "命中技能、缺失技能、规则说明", "已完成"],
        ["可视化", "Streamlit 筛选、图表、下载", "已完成"],
        ["HDFS", "raw_data、cleaned_data、results", "已完成"],
        ["PySpark", "读取、清洗、去重、写回", "已完成"],
        ["MLlib", "Word2Vec 特征写入 Parquet", "已完成"],
        ["工程验证", "11 项单元测试与 35 个教学案例", "已完成"],
        ["交付文档", "README、报告、答辩 PPT、截图", "已完成"],
    ]
    add_table(document, ["任务书要求", "对应实现", "状态"], checklist, [1.25, 4.25, 0.75])

    add_heading(document, "使用场景", level=2)
    add_bullets(
        document,
        [
            "学生选择个人简历后查看 Top N 岗位、七维得分、匹配技能和提升建议。",
            "招聘方选择岗位后查看 Top N 候选人，并比较技能、语义和硬性条件。",
            "教师或开发者可上传自定义 CSV，调整 Top N、最低分与城市筛选，并下载当前结果。",
        ],
    )
    document.add_page_break()

    add_heading(document, "二 系统架构")
    add_text(
        document,
        "系统分为数据层、计算层和交互层。Docker Compose 启动单节点 Hadoop 与 YARN，并把 day2 项目目录挂载到容器的 /workspace/resume_matching_project。算法结果既保存在本地 output，也回写 HDFS 供大数据流程继续使用。",
    )
    architecture = document.add_table(rows=1, cols=7)
    architecture.alignment = WD_ALIGN_PARAGRAPH.CENTER
    flow = [
        ("CSV 数据", PALE_BLUE),
        ("→", WHITE),
        ("预处理", PALE_BLUE),
        ("→", WHITE),
        ("相似度与规则", PALE_BLUE),
        ("→", WHITE),
        ("Top N 与界面", PALE_BLUE),
    ]
    widths = [0.86, 0.25, 0.86, 0.25, 1.42, 0.25, 1.25]
    for cell, (text, fill), width in zip(architecture.rows[0].cells, flow, widths):
        cell.text = text
        cell.width = Inches(width)
        set_cell_shading(cell, fill)
        set_cell_border(cell, BLUE if text != "→" else WHITE)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cell.paragraphs[0].runs:
            set_run_font(run, size=9.5, bold=True, color=BLUE)

    add_heading(document, "模块职责", level=2)
    modules = [
        ["preprocess.py", "分词、停用词、技能别名、匹配文本构造"],
        ["similarity.py", "统一语料训练 TF-IDF 与 Word2Vec，生成余弦相似矩阵"],
        ["scoring.py", "规则维度、权重合成、自然语言推荐理由"],
        ["matcher.py", "全量笛卡尔积、双向排名、三份 CSV 导出"],
        ["spark_job.py", "HDFS 读取、PySpark 清洗、MLlib Word2Vec 特征"],
        ["app.py", "双向交互、筛选、图表、下载"],
    ]
    add_table(document, ["文件", "职责"], modules, [1.45, 4.8])

    add_heading(document, "目录组织", level=2)
    add_code_block(
        document,
        [
            "resume_matching_project/",
            "├── data/               # 简历、岗位、停用词、技能别名",
            "├── src/                # 预处理、算法、HDFS、PySpark",
            "├── output/             # 全量与双向 Top N 结果",
            "├── tests/              # 回归测试",
            "├── docs/               # 报告、PPT、设计稿、截图",
            "├── app.py              # Streamlit",
            "└── run_pipeline.py     # 本地与大数据一键流程",
        ],
    )
    document.add_page_break()

    add_heading(document, "三 数据设计与质量控制")
    add_text(
        document,
        "示例数据覆盖大数据、数据分析、Java 后端、云运维、自然语言处理、计算机视觉、前端和数据仓库等方向。技能和证书使用分号分隔，数值字段使用年限和月薪。数据量达到任务书建议范围，同时保持每一行都能人工审阅。",
    )
    resume_fields = [
        ["resume_id", "简历唯一编号", "必需"],
        ["name", "学生姓名", "必需"],
        ["education / major", "学历与专业", "学历必需"],
        ["skills", "分号分隔技能", "必需"],
        ["experience_years", "经验年限", "必需"],
        ["city", "当前或期望城市", "必需"],
        ["expected_salary", "期望月薪", "可选"],
        ["certificates", "证书列表", "可选"],
        ["project_experience", "项目经历文本", "可选"],
        ["self_description", "自我描述文本", "可选"],
    ]
    job_fields = [
        ["job_id", "岗位唯一编号", "必需"],
        ["job_title / company", "岗位名称与公司", "必需"],
        ["required_education", "最低学历", "必需"],
        ["required_skills", "分号分隔技能要求", "必需"],
        ["min_experience_years", "最低经验年限", "必需"],
        ["city", "工作城市", "必需"],
        ["salary", "岗位月薪", "可选"],
        ["preferred_certificates", "优先证书", "可选"],
        ["job_description", "岗位描述文本", "可选"],
    ]
    add_heading(document, "简历字段", level=2)
    add_table(document, ["字段", "含义", "约束"], resume_fields, [2.0, 3.45, 0.8])
    add_heading(document, "岗位字段", level=2)
    add_table(document, ["字段", "含义", "约束"], job_fields, [2.1, 3.35, 0.8])

    add_heading(document, "质量规则", level=2)
    add_bullets(
        document,
        [
            "缺少必需列时直接报错，避免模型在字段意义不明时继续运行。",
            "空白可选列补为空字符串，无法解析的经验和薪资按 0 处理并限制为非负数。",
            "按 resume_id 或 job_id 去重，保证全量配对数量可预测。",
            "CSV 使用 UTF-8-SIG 导出，Windows Excel 可直接识别中文。",
        ],
    )

    add_heading(document, "四 文本预处理")
    add_text(
        document,
        "自然语言与结构化技能分别处理。skills 和 required_skills 先按中英文分隔符拆分，再通过 skill_alias.json 归一；项目经历和岗位描述使用 jieba 精确分词，移除停用词和无意义符号。技能字段在匹配文档中重复一次，使可信的结构化字段比一般描述具有更高影响。",
    )
    add_numbered(
        document,
        [
            "把英文转换为小写，并统一 Python3、PySpark、Power BI、K8s、SpringBoot 等写法。",
            "用 jieba 对中文描述分词，保留英文技能、数字和常见技术符号。",
            "过滤停用词、标点和无意义单字，同时保留 C、R 等合法单字符技能。",
            "把技能、专业、项目经历、自我描述或岗位描述拼接为匹配文档。",
        ],
    )
    add_heading(document, "标准化示例", level=2)
    add_table(
        document,
        ["原始写法", "标准技能"],
        [
            ["PySpark / Apache Spark / Spark SQL", "spark"],
            ["Power BI / PowerBI", "powerbi"],
            ["K8s", "kubernetes"],
            ["SpringBoot / Spring Boot", "spring boot"],
            ["scikit-learn / 机器学习", "sklearn"],
        ],
        [3.5, 2.75],
    )
    add_text(
        document,
        "边界说明：当前别名采用课程数据可控的字符串替换。真实系统应使用词边界、词典版本管理和人工审核，避免短别名误替换其他单词。",
    )
    document.add_page_break()

    add_heading(document, "五 相似度与多维评分")
    add_heading(document, "TF-IDF", level=2)
    add_text(
        document,
        "TF-IDF 对所有简历和岗位的统一语料拟合，并使用一元词与二元词。余弦相似度衡量两个稀疏向量的方向接近程度。该分数能直接反映 Python、Spark、SQL 等关键词和短语的重合，但无法单独处理同义表达。",
    )
    add_code_block(
        document,
        [
            "TF-IDF(t,d) = TF(t,d) × log((N + 1) / (DF(t) + 1)) + 1",
            "cosine(A,B) = (A · B) / (||A|| × ||B||)",
        ],
    )
    add_heading(document, "Word2Vec", level=2)
    add_text(
        document,
        "gensim Word2Vec 使用全部分词文档训练 80 维 Skip-gram 模型。句向量取文档中可用词向量的平均值，再计算简历与岗位的余弦相似度。为保证课堂复现，训练固定随机种子 42 且 workers=1。PySpark 链路另用 MLlib Word2Vec 生成 60 维特征并写入 HDFS Parquet。",
    )
    add_heading(document, "七维总分", level=2)
    formula_rows = [
        ["技能覆盖", "30%", "简历技能对岗位要求的覆盖率"],
        ["TF-IDF", "20%", "关键词与短语重合"],
        ["Word2Vec", "15%", "平均词向量语义接近"],
        ["学历", "15%", "达到要求得满分，差一级递减 35"],
        ["经验", "10%", "实际年限与最低年限之比，上限 100"],
        ["城市", "5%", "一致或岗位不限得满分"],
        ["证书", "5%", "优先证书覆盖率；无要求得满分"],
    ]
    add_table(document, ["维度", "权重", "计算依据"], formula_rows, [1.2, 0.7, 4.35])
    add_text(
        document,
        "综合分 = 0.30×技能 + 0.20×TF-IDF + 0.15×Word2Vec + 0.15×学历 + 0.10×经验 + 0.05×城市 + 0.05×证书。薪资分作为独立诊断写入结果，不进入默认总分。",
    )
    document.add_page_break()

    add_heading(document, "六 排名与可解释结果")
    add_text(
        document,
        "matcher.py 对每份简历和每个岗位做全量配对，再分别按 resume_id 和 job_id 分组排序。总分相同的记录按稳定 ID 顺序排列，因此重复运行可得到一致排名。导出阶段可以设置 Top N 与最低技能分门槛。",
    )
    add_table(
        document,
        ["结果文件", "视角", "用途"],
        [
            ["full_matches.csv", "全量", "144 组配对、全部分数与双向名次"],
            ["top_matches.csv", "学生", "每名学生的 Top N 岗位"],
            ["top_candidates.csv", "岗位", "每个岗位的 Top N 候选人"],
        ],
        [1.7, 0.85, 3.7],
    )
    add_heading(document, "解释生成规则", level=2)
    add_bullets(
        document,
        [
            "列出命中的核心技能和岗位仍要求的缺失技能。",
            "明确学历、经验、城市、证书和薪资是否满足。",
            "根据 TF-IDF 与 Word2Vec 的平均值把语义相关度分为高、部分和较低。",
            "推荐理由与各维度数值同时输出，避免只给一个无法复核的总分。",
        ],
    )
    example = top.iloc[0]
    add_heading(document, "示例结果", level=2)
    add_table(
        document,
        ["学生", "Top 1 岗位", "综合分", "命中技能", "缺失技能"],
        [[example["student_name"], example["job_title"], f"{example['total_score']:.2f}", example["matched_skills"], example["missing_skills"]]],
        [0.65, 1.35, 0.65, 1.55, 1.55],
    )
    add_text(document, str(example["reason"]))
    document.add_page_break()

    add_heading(document, "七 HDFS 与 PySpark 数据链路")
    add_text(
        document,
        "run_pipeline.py --with-hdfs 依次执行本地匹配、HDFS 原始数据上传、PySpark 清洗、MLlib Word2Vec 和匹配结果回写。HDFS 根目录为 /resume_matching，原始数据、清洗数据和结果分开存放。",
    )
    add_code_block(
        document,
        [
            "/resume_matching/",
            "├── raw_data/resumes.csv, jobs.csv",
            "├── cleaned_data/resumes, jobs, word2vec_features",
            "└── results/full_matches.csv, top_matches.csv, top_candidates.csv, spark_summary",
        ],
    )
    add_picture(document, "hdfs-resume-matching.png", "图 1  HDFS 中的 resume_matching 三级目录")
    add_text(
        document,
        "PySpark 使用 header 与 inferSchema 读取 HDFS CSV，按业务 ID 去重并补齐空值，生成 match_text 后以 CSV 写回 cleaned_data。MLlib Word2Vec 在简历与岗位联合语料上训练，并把 entity_id、tokens 和 features 以 Parquet 保存。实测 Spark 汇总为 resumes=12、jobs=12。",
    )
    document.add_page_break()

    add_heading(document, "八 大数据运行证据")
    add_picture(document, "yarn-nodes.png", "图 2  YARN 节点页面显示 1 个 RUNNING 节点和 3 GB 可用内存")
    add_picture(document, "spark-jobs.png", "图 3  Spark 3.5.1 本地任务完成 3 个作业")
    add_text(
        document,
        "镜像健康检查同时访问 NameNode 9870 与 ResourceManager 8088。容器内 jps 实测包含 NameNode、DataNode、SecondaryNameNode、ResourceManager 和 NodeManager。Spark 运行时使用 Java 8u502，并在 4040 页面显示完成的 Job 与 Stage。",
    )
    document.add_page_break()

    add_heading(document, "九 Streamlit 交互系统")
    add_text(
        document,
        "界面使用深海军蓝导航、白色信息卡和钴蓝强调色。侧栏提供上传、Top N 和最低分控制；主区先展示对象摘要与 Top 1，再展示核心分数、技能标签、推荐理由、七维条形图和完整列表。移动端自动收起侧栏，主内容改为单列。",
    )
    add_picture(document, "streamlit-student-desktop.png", "图 4  学生找岗位桌面视图")
    document.add_page_break()
    add_picture(document, "streamlit-job-desktop.png", "图 5  岗位找人才桌面视图")
    add_picture(document, "streamlit-student-mobile.png", "图 6  390×844 移动端自适应视图", width=2.25)
    document.add_page_break()

    add_heading(document, "十 实验结果")
    add_text(
        document,
        f"全量配对平均分为 {full['total_score'].mean():.2f}。每名学生的 Top 1 平均分为 {top['total_score'].mean():.2f}，范围为 {top['total_score'].min():.2f} 至 {top['total_score'].max():.2f}。全量结果中技能覆盖不低于 60 分的配对有 {(full['skill_score'] >= 60).sum()} 组。",
    )
    result_rows = [
        [
            row.resume_id,
            row.student_name,
            row.job_title,
            f"{row.total_score:.2f}",
            f"{row.skill_score:.0f}",
        ]
        for row in top.itertuples()
    ]
    add_table(document, ["简历", "学生", "Top 1 岗位", "综合分", "技能分"], result_rows, [0.6, 0.65, 2.45, 0.75, 0.75])
    add_heading(document, "结果观察", level=2)
    add_bullets(
        document,
        [
            "Java 后端、云运维、计算机视觉、前端和数据仓库方向的结构化技能覆盖均达到 100，Top 1 综合分在 87 分以上。",
            "陈晨与大数据开发岗位的技能覆盖为 60，语义和规则分补充了项目经历、学历、经验与城市信息，最终综合分为 67.40。",
            "12 个 Top 1 的学历、经验与城市分均为 100；该结果源于示例数据按方向设计，不能直接推断模型在真实招聘数据上的准确率。",
        ],
    )
    document.add_page_break()

    add_heading(document, "十一 测试与复现")
    add_text(
        document,
        "自动化测试覆盖预处理、规则边界、数据规模、全量配对、排序与导出。day2 项目共 7 项测试，day2-3 教学案例共 4 项测试；另按讲义顺序完整运行 35 个案例，其中包括 PySpark Word2Vec。",
    )
    add_table(
        document,
        ["验证项", "实测结果"],
        [
            ["镜像构建", "Docker Compose 构建成功"],
            ["Hadoop 进程", "5 个核心服务进程正常"],
            ["day2 单元测试", "7/7 通过"],
            ["day2-3 单元测试", "4/4 通过"],
            ["教学案例", "35/35 通过"],
            ["本地匹配", "12×12=144 组，三份 CSV 生成"],
            ["HDFS 与 Spark", "上传、清洗、MLlib、回写成功"],
            ["Streamlit", "双向视图、筛选、图表、下载、移动端通过"],
            ["浏览器控制台", "未发现 error 或 warn"],
        ],
        [2.0, 4.25],
    )
    add_heading(document, "复现命令", level=2)
    add_code_block(
        document,
        [
            "cd day1/hadoop-spark-docker",
            "docker compose build bigdata",
            "docker compose up -d",
            "docker compose exec -T bigdata bash -lc \\",
            "  'cd /workspace/resume_matching_project && python run_pipeline.py --with-hdfs'",
            "docker compose exec bigdata bash -lc \\",
            "  'cd /workspace/resume_matching_project && streamlit run app.py'",
        ],
    )
    document.add_page_break()

    add_heading(document, "十二 局限与改进方向")
    add_bullets(
        document,
        [
            "当前 Word2Vec 只在 24 篇教学文档上训练，适合展示流程，不代表生产级语义效果。可换用大规模招聘语料或经审计的中文嵌入模型。",
            "技能覆盖按集合等权计算，尚未区分核心技能、加分技能和熟练度。可在岗位数据中增加技能权重与等级。",
            "默认权重来自任务书示例和课程可解释性要求，尚未用真实录用结果标定。后续可通过人工标注、排序指标和交叉验证调整。",
            "城市采用精确匹配，未考虑远程、通勤圈和迁移意愿。薪资只做诊断，不进入总分。",
            "真实招聘涉及公平性、隐私与合规。系统应屏蔽与岗位无关的敏感属性，记录推荐依据，并保留人工复核和申诉机制。",
        ],
    )
    add_heading(document, "可执行改进", level=2)
    add_numbered(
        document,
        [
            "收集匿名化且经过授权的历史职位与简历文本，建立训练集和人工相关性标签。",
            "采用 NDCG、Recall@K 和人工一致率评估双向排序，而不是只观察示例 Top 1。",
            "为技能、证书、城市和薪资增加可配置规则，并在界面中显示权重变化。",
            "增加访问控制、数据脱敏、模型版本和审计日志，再考虑用于真实业务。",
        ],
    )

    add_heading(document, "参考资料")
    references = [
        "学生项目任务书：基于大数据+AI的简历-岗位人才匹配系统.pdf",
        "文本匹配小案例一：jieba 分词、停用词、技能词标准化.pdf",
        "文本匹配小案例二：词袋、TF-IDF 与余弦相似度.pdf",
        "文本匹配小案例三：Word2Vec 词向量与语义相似度.pdf",
        "文本匹配小案例四：多维评分与可解释匹配.pdf",
        "项目源码 README.md 与本地运行日志",
    ]
    add_numbered(document, references)
    return document


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    report = build_report()
    report.save(OUTPUT)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
