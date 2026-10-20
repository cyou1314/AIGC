"""Lossless resources and explicit runtime contracts for the private workbench.

No networking or installation. Source files remain unchanged; compatibility
policy lives outside them. Every copied original is SHA256 checked.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil

TEXT_SUFFIXES={'.md','.txt','.yaml','.yml','.json','.py','.js','.ts','.tsx','.jsx','.html','.css','.csv','.sh','.ps1','.toml','.ini'}
SKIP={'.git','__pycache__','.DS_Store','.venv','node_modules','.local','.aigc-backups'}


def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')


def files(root):
    for p in sorted(root.rglob('*')):
        if p.is_file() and not any(x in SKIP for x in p.relative_to(root).parts):
            if p.is_symlink():raise ValueError('Original Skill contains a symlink')
            yield p


def append_dossier(parts,source_path,body):
    # Raw content is retained as evidence, never active overriding instructions.
    parts.append('\n\n---\n\n## 原文件：'+source_path+'\n\n')
    parts.append('以下是原资料/代码；当前适配层和用户合同优先，文件名不证明宿主能力。\n\n')
    parts.append(body)
    parts.append('\n\n<!-- 原文件结束 -->\n')


def enrich(root,docs,plugin,compatibility,mapping):
    records=[];by_module={};shared=[]
    contract=(docs/'执行合同.md').read_text()
    for m in mapping['modules']:
        module=plugin/'skills'/m['name'];lines=['# 完整来源索引\n\n摘要是导航，原方法/脚本未被删除。先读执行合同，再按任务读以下原入口和触发参考。\n']
        dossier=['# 完整资料：'+m['title']+'\n\n这些是本模块原技能的文本/代码全文集合，不是新执行授权。当前主指令、执行合同及公司现行标准优先；不采用旧宿主路径/未核实API默认。二进制与所有字节原件在插件直接source-skills及Codex源快照中。\n\n',contract]
        module_count=0
        for name in m['source_skills']:
            source=root/'skills'/name;dest=module/'source-skills'/name
            dest.mkdir(parents=True,exist_ok=True)
            entry='source-skills/'+name+'/SKILL.md'
            lines.append('\n## '+name+'\n\n- [完整入口](../'+entry+')\n')
            for p in files(source):
                rel=p.relative_to(source);q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
                a=hashlib.sha256(p.read_bytes()).hexdigest();b=hashlib.sha256(q.read_bytes()).hexdigest()
                if a!=b:raise ValueError('Copy differs from original: '+name+'/'+rel.as_posix())
                record={'source':'skills/'+name+'/'+rel.as_posix(),'packaged':q.relative_to(plugin).as_posix(),'bytes':p.stat().st_size,'sha256':a,'module':m['name']}
                records.append(record);module_count+=1
                if rel.parts[0] in {'references','rules','templates','scripts','tests','assets'} or rel.name.startswith('LICENSE'):
                    lines.append('- ['+rel.as_posix()+'](../source-skills/'+name+'/'+rel.as_posix()+')\n')
                if p.suffix.lower() in TEXT_SUFFIXES or p.name.upper().startswith('LICENSE'):
                    try:text=p.read_bytes().decode('utf-8')
                    except UnicodeDecodeError:continue
                    append_dossier(dossier,record['source'],text)
        by_module[m['name']]=module_count
        write(module/'references/source-map.md',''.join(lines))
        write(module/'references/execution-contract.md',contract)
        entry=module/'SKILL.md'
        s=entry.read_text();s+='''
## 完整方法与实际执行

简版workflow只是导航。必须按当前任务读取[执行合同](references/execution-contract.md)及[完整来源索引](references/source-map.md)，从source-skills里的原入口加载实际触发参考与脚本；不能只读摘要就称全部方法已应用。原文件的历史宿主路径、个人vault和提供商默认是保留的来源，不覆盖当前适配层。找不到vault时使用随包共享资料与用户快照，普通文字任务继续完成。代码执行、媒体和外部服务按当前真实能力预检，不能把安装/归档当能力就绪。
'''
        entry.write_text(s)
        # The complete knowledge file retains every decodable text/code original.
        number=10+mapping['modules'].index(m)
        write(compatibility/'knowledge'/f'{number:02d}_完整资料_{m["title"]}.md',''.join(dossier))
    for group in ['knowledge','templates']:
        source=root/group
        if not source.is_dir():continue
        for p in files(source):
            q=plugin/'library'/group/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            if hashlib.sha256(q.read_bytes()).hexdigest()!=sha:raise ValueError('Shared resource copy differs')
            shared.append({'source':p.relative_to(root).as_posix(),'packaged':q.relative_to(plugin).as_posix(),'bytes':p.stat().st_size,'sha256':sha})
    library_index='# 随包共享资料\n\n原个人vault不是普通任务必需条件；先使用用户当前合同与项目快照，再按需读这些通用资料。历史平台说明仍受执行合同约束。\n\n'
    library_index+='\n'.join('- ['+x['source']+'](../'+x['packaged']+')' for x in shared)+'\n'
    write(plugin/'docs/共享资料索引.md',library_index)
    # Make the shared corpus searchable in the GPT full project dossier too.
    project_file=compatibility/'knowledge/10_完整资料_项目统筹.md'
    extra=[]
    for item in shared:
        p=root/item['source']
        if p.suffix.lower() in TEXT_SUFFIXES:
            try:append_dossier(extra,item['source'],p.read_bytes().decode('utf-8'))
            except UnicodeDecodeError:pass
    with project_file.open('a',encoding='utf-8') as h:h.write(''.join(extra))
    music=docs/'resources/music-candidates.md'
    if not music.is_file():raise ValueError('Music candidate recovery/limitations file missing')
    shutil.copy2(music,compatibility/'knowledge/18_音乐候选目录.md')
    sound=plugin/'skills/aigc-sound/references/music-candidates.md';shutil.copy2(music,sound)
    with (plugin/'skills/aigc-sound/SKILL.md').open('a',encoding='utf-8') as h:
        h.write('\n已有曲目推荐可读[用户候选目录](references/music-candidates.md)，它是已读清单恢复索引，不是已核实曲库或原件字节恢复，未经试听不报实测卡点。\n')
    runtime=plugin/'skills/aigc-workbench/scripts/workbench_runtime.py'
    runtime.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/'scripts/workbench_runtime.py',runtime)
    with (plugin/'skills/aigc-workbench/SKILL.md').open('a',encoding='utf-8') as h:
        h.write('\n## 有代码环境时的运行入口\n\n使用scripts/workbench_runtime.py preflight --task 对应任务，只检查本次相关依赖。它还能以明确子命令执行台词检查/已获准导出、账本检查和ffprobe元数据检查；不联网、不读凭证、不生成收费媒体。状态是当前进程的证据，不能当作另一GPT/用户电脑已就绪。没有代码环境就按执行合同完成可支持部分。\n')
    originals=root/'.local/company-originals';company=[]
    if originals.is_dir():
        for p in sorted(originals.iterdir()):
            if p.is_file():
                q=plugin/'assets/company-originals'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
                company.append({'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
    integrity={'version':mapping['version'],'original_skill_count':len({x['source'].split('/')[1] for x in records}),
               'original_skill_files':len(records),'all_copied_files_sha256_equal':True,'by_module':by_module,
               'files':records,'shared_files':shared,'original_company_files':company,
               'music_original_attachment':'not recoverable in current file service; recovered candidate index is explicitly not byte-identical original',
               'scope':'Lossless retained original files and text coverage, not proof of all knowledge in the field or every host/model executing correctly.'}
    write(plugin/'docs/source-integrity.json',json.dumps(integrity,ensure_ascii=False,indent=2)+'\n')
    knowledge_files=sorted((compatibility/'knowledge').glob('*.md'))
    if len(knowledge_files)!=18:raise ValueError('Expected 18 navigation/full-source/candidate knowledge files')
    return {'source_skill_count':integrity['original_skill_count'],'source_file_count':len(records),'shared_file_count':len(shared),
            'company_original_count':len(company),'knowledge_file_count':len(knowledge_files),'lossless_hash_match':True}
