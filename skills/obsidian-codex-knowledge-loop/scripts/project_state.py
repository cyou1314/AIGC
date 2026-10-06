#!/usr/bin/env python3
"""Persistent AIGC state: type-specific contracts and real-file receipts."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'aigc-production-router/scripts'))
from workflow_paths import runtime_paths, shanghai_timezone

WORKSPACE, VAULT, OUTPUTS = runtime_paths()
CATALOG = Path(__file__).resolve().parents[2] / 'aigc-production-router/references/production-profiles.json'
ALLOWED = {'候选', '采用', '成片', '废弃'}
QC = {'未请求', '待核验', '通过', '返修', '用户确认'}
RH = '| 镜头/Block | 提示词版本 | 生成文件 | 状态 | 日期 |'
DH = '| 交付物 | 版本 | 文件 | 证据类型 | 核验状态 | 证据路径 | 日期 |'

def today():
    return dt.datetime.now(shanghai_timezone()).date().isoformat()

def single_line(value):
    if '\n' in value or '\r' in value:
        raise ValueError('字段必须是单行文本')
    return value

def cell(value):
    return single_line(str(value)).replace('|', '&#124;')

def safe_name(value):
    value = re.sub(r'[\\/:*?"<>|]+', '-', single_line(value)).strip().strip('.')
    if not value:
        raise ValueError('项目名不能为空')
    return value

def profiles():
    return json.loads(CATALOG.read_text(encoding='utf-8'))['profiles']

def real_file(value):
    path = Path(single_line(value)).expanduser()
    if not path.is_absolute():
        raise ValueError('请提供文件绝对路径')
    path = path.resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f'文件不存在或为空：{path}')
    return str(path)

def write_page(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        stream.write(text)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

def read_project(value):
    path = Path(value).expanduser().resolve()
    return path, path.read_text(encoding='utf-8')

def field(text, name, value, optional=False):
    single_line(value)
    pattern = re.compile(rf'^(- {re.escape(name)}：).*$', re.M)
    if not pattern.search(text):
        if optional:
            return text
        raise ValueError(f'缺少字段：{name}')
    return pattern.sub(lambda m: m.group(1) + value, text, count=1)

def refresh(text):
    return re.sub(r'^updated:.*$', f'updated: {today()}', text, count=1, flags=re.M)

def table_match(text, heading):
    match = re.search(rf'^## {re.escape(heading)}[ \t]*\n([\s\S]*?)(?=^## |\Z)', text, re.M)
    if not match:
        raise ValueError(f'缺少章节：{heading}')
    return match

def rows(text, heading, width):
    result = []
    for line in table_match(text, heading).group(1).splitlines():
        if not line.startswith('|'):
            continue
        values = [v.strip() for v in line.strip('|').split('|')]
        if values[0] in {'镜头/Block', '交付物'} or all(re.fullmatch(r':?-+:?', v) for v in values):
            continue
        if len(values) != width:
            raise ValueError(f'{heading}表格列数错误')
        result.append(values)
    return result

def upsert(text, heading, header, values):
    if f'## {heading}' not in text:
        text += f'\n\n## {heading}\n\n{header}\n|' + '---|' * len(values) + '\n'
    existing = rows(text, heading, len(values))
    # Identity: block/item + version + real absolute path. Status transitions update one row.
    for i, row in enumerate(existing):
        if row[:3] == values[:3]:
            existing[i] = values
            break
    else:
        existing.append(values)
    match = table_match(text, heading)
    notes = [line for line in match.group(1).splitlines() if line.strip() and not line.startswith('|')]
    content = '\n' + header + '\n|' + '---|' * len(values) + '\n'
    content += '\n'.join('| ' + ' | '.join(row) + ' |' for row in existing) + '\n\n'
    if notes:
        content += '\n'.join(notes) + '\n\n'
    return text[:match.start(1)] + content + text[match.end(1):]

def init_project(a):
    profile = profiles().get(a.domain)
    if a.domain != 'pending' and profile is None:
        raise ValueError(f'未知生产类型：{a.domain}')
    for value in [a.name, a.format, a.goal, a.next, a.deliverable, a.budget, a.authority, a.lead or '']:
        single_line(value)
    path = Path(a.vault).expanduser().resolve() / 'projects' / f'{safe_name(a.name)}.md'
    if path.exists():
        if not a.force:
            print(path)
            return
        suffix = dt.datetime.now(shanghai_timezone()).strftime('%Y%m%d-%H%M%S-%f')
        shutil.copy2(path, path.with_name(path.name + '.backup-' + suffix))
    root = Path(a.output_root).expanduser().resolve() / safe_name(a.name)
    lead = a.lead or (profile['lead'] if profile else 'aigc-production-router')
    label = profile['label'] if profile else '待判断'
    acceptance = '；'.join(profile['acceptance']) if profile else '待选择生产类型'
    text = f'''---
type: project
schema_version: 2
domain: {a.domain}
status: active
format: {json.dumps(a.format, ensure_ascii=False)}
project_root: {json.dumps(str(root), ensure_ascii=False)}
updated: {today()}
knowledge_cycle: fast
tags: [项目]
---

# {a.name}

## 当前快照

- 生产类型：{a.domain}（{label}）
- 当前目标：{a.goal}
- 当前阶段：启动
- 当前有效提示词：未建立/本类型不需要时不适用
- 当前权威输入与版本：{a.authority}
- 最近生成文件：无
- 唯一下一步：{a.next}
- 当前阻塞：无

## 当前知识胶囊

- 当前片型：{a.format}
- 主导Skill：{lead}
- 协作Skill：仅按当前动作触发
- 当前必读知识：[[agent/跨类型AIGC生产工作流]]
- 条件知识：当前生产类型的验收标准与主Skill
- 当前真实素材：{a.authority}
- 已确认约束：用户要求与权威输入优先；各类证据分别登记
- 最近核验：{today()}

## 制作合同

- 本轮交付物：{a.deliverable}
- 用途/渠道/受众：待确认
- 输出规格：以用户要求或主Skill的已核验默认值为准
- 已确认预算：{a.budget}
- 本类型完成条件：{acceptance}
- 时间/次数/费用：未知，发生后按证据登记

## 结果

- 当前输出：无
- 成片位置：无/本类型不适用
- 项目状态：进行中
- 质量分析：未请求
- 下次从这里继续：{a.next}

## 生成回执

{RH}
|---|---|---|---|---|

只在真实生成后登记；状态：候选 / 采用 / 成片 / 废弃。非视频最终资产用“采用”。

## 交付回执

{DH}
|---|---|---|---|---|---|---|

文本、文件、生成结果分别登记。“通过”要求检查证据，不从文件存在自动推出。

## 知识候选

- 候选：
- 依据：
- 状态：待验证
'''
    write_page(path, text)
    print(path)

def snapshot(a):
    path, text = read_project(a.project)
    for name, value in [('当前目标', a.goal), ('当前阶段', a.stage), ('唯一下一步', a.next),
                        ('当前阻塞', a.blocker), ('当前权威输入与版本', a.authority), ('主导Skill', a.lead)]:
        if value is not None:
            text = field(text, name, value)
    if a.next is not None:
        text = field(text, '下次从这里继续', a.next, optional=True)
    if a.authority is not None:
        text = field(text, '当前真实素材', a.authority, optional=True)
    text = field(text, '最近核验', today(), optional=True)
    write_page(path, refresh(text))
    print(path)

def receipt(a):
    if a.status not in ALLOWED:
        raise ValueError('状态必须是：候选 / 采用 / 成片 / 废弃')
    path, text = read_project(a.project)
    output = real_file(a.file)
    if a.status == '成片' and Path(output).suffix.lower() not in {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'}:
        raise ValueError('非视频资产使用“采用”，不标记“成片”')
    text = upsert(text, '生成回执', RH, [cell(a.block), cell(a.prompt_version), cell(output), a.status, today()])
    text = field(text, '最近生成文件', output, optional=True)
    write_page(path, refresh(text))
    print(path)

def delivery(a):
    if a.qc not in QC:
        raise ValueError('未知核验状态')
    path, text = read_project(a.project)
    output = real_file(a.file)
    evidence = real_file(a.evidence) if a.evidence else '无'
    if a.qc in {'通过', '用户确认'} and evidence == '无':
        raise ValueError('核验通过或用户确认必须提供实际检查/确认记录文件')
    values = [cell(a.item), cell(a.version), cell(output), a.kind, a.qc, cell(evidence), today()]
    text = upsert(text, '交付回执', DH, values)
    text = field(text, '当前输出', output, optional=True)
    write_page(path, refresh(text))
    print(path)

def validate(a):
    path, text = read_project(a.project)
    errors = [f'缺少 {v}' for v in ['## 当前快照', '## 当前知识胶囊', '## 生成回执', '- 唯一下一步：'] if v not in text]
    for row in rows(text, '生成回执', 5):
        if row[3] not in ALLOWED:
            errors.append('非法生成状态')
        if a.check_files:
            real_file(row[2].replace('&#124;', '|'))
    if '## 交付回执' in text:
        for row in rows(text, '交付回执', 7):
            if row[3] not in {'文本', '文件', '生成结果'} or row[4] not in QC:
                errors.append('非法交付类型或核验状态')
            if row[4] in {'通过', '用户确认'} and row[5] == '无':
                errors.append('核验缺少证据')
            if a.check_files:
                real_file(row[2].replace('&#124;', '|'))
                if row[5] != '无':
                    real_file(row[5].replace('&#124;', '|'))
    if 'schema_version: 2' in text:
        match = re.search(r'^domain: (.+)$', text, re.M)
        if not match or match.group(1) not in set(profiles()) | {'pending'}:
            errors.append('未知生产类型')
        if '## 制作合同' not in text:
            errors.append('缺少制作合同')
    if errors:
        raise ValueError('; '.join(errors))
    print(f'VALID {path} (state structure only; creative acceptance not implied)')

def build_parser():
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init')
    p.add_argument('--name', required=True); p.add_argument('--format', default='待判断')
    p.add_argument('--domain', default='pending'); p.add_argument('--goal', required=True)
    p.add_argument('--lead'); p.add_argument('--next', required=True)
    p.add_argument('--deliverable', default='依本轮目标确定'); p.add_argument('--budget', default='未知')
    p.add_argument('--authority', default='待登记'); p.add_argument('--vault', default=str(VAULT))
    p.add_argument('--output-root', default=str(OUTPUTS)); p.add_argument('--force', action='store_true')
    p.set_defaults(func=init_project)
    p = sub.add_parser('snapshot'); p.add_argument('--project', required=True)
    for key in ['goal', 'stage', 'next', 'blocker', 'authority', 'lead']:
        p.add_argument('--' + key)
    p.set_defaults(func=snapshot)
    p = sub.add_parser('receipt'); p.add_argument('--project', required=True); p.add_argument('--block', required=True)
    p.add_argument('--prompt-version', required=True); p.add_argument('--file', required=True)
    p.add_argument('--status', required=True); p.set_defaults(func=receipt)
    p = sub.add_parser('delivery'); p.add_argument('--project', required=True); p.add_argument('--item', required=True)
    p.add_argument('--version', required=True); p.add_argument('--file', required=True)
    p.add_argument('--kind', choices=['文本', '文件', '生成结果'], default='文件')
    p.add_argument('--qc', default='未请求'); p.add_argument('--evidence'); p.set_defaults(func=delivery)
    p = sub.add_parser('validate'); p.add_argument('--project', required=True)
    p.add_argument('--check-files', action='store_true'); p.set_defaults(func=validate)
    return root

if __name__ == '__main__':
    args = build_parser().parse_args()
    try:
        args.func(args)
    except (ValueError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(2)
