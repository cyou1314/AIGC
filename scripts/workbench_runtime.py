#!/usr/bin/env python3
"""Offline AIGC workbench preflight and bounded local helpers.

No network, credential reads, install, external publishing or paid generation.
Readiness is evidence about this process, not another ChatGPT host. Provider
readiness must be checked with the real connected tool in the current task.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys

TASKS = {
 'script': ('aigc-writing','text',()),
 'video-prompt': ('aigc-directing','text',()),
 'prompt-review': ('aigc-review','text',()),
 'poster-prompt': ('aigc-visuals','text',()),
 'commercial-script': ('aigc-commercial-digital','text',()),
 'music-prompt': ('aigc-sound','text',()),
 'lines-extract': ('aigc-sound','file',()),
 'media-inspect': ('aigc-postproduction','file',('ffprobe',)),
 'media-edit': ('aigc-postproduction','file',('ffmpeg','ffprobe')),
 'editor-project': ('aigc-postproduction','handoff',()),
 'image-generate': ('aigc-visuals','provider',()),
 'video-generate': ('aigc-directing','provider',()),
 'audio-generate': ('aigc-sound','provider',()),
 'transcribe': ('aigc-sound','provider',()),
 'video-qc': ('aigc-review','inspection',()),
 'image-qc': ('aigc-review','inspection',()),
 'web-ui': ('aigc-commercial-digital','implementation',()),
}


def find_root(explicit=None):
    if explicit:
        root=Path(explicit).expanduser().resolve()
        if not (root/'plugin.json').is_file():
            raise ValueError('Provided plugin root has no plugin.json')
        return root
    for root in Path(__file__).resolve().parents:
        if (root/'plugin.json').is_file(): return root
    raise ValueError('Run from the extracted plugin or pass --plugin-root')


def preflight(task, input_path=None):
    module,kind,bins=TASKS[task]
    source=Path(input_path).expanduser().resolve() if input_path else None
    dependencies=[{'name':x,'available':bool(shutil.which(x))} for x in bins]
    if source and source.suffix.lower()=='.xlsx' and task=='lines-extract':
        dependencies.append({'name':'openpyxl','available':importlib.util.find_spec('openpyxl') is not None})
    missing=[d['name'] for d in dependencies if not d['available']]
    requires_file=kind in {'file','inspection'}
    blockers=[]
    if requires_file and source is None:blockers.append('source-not-supplied')
    elif source and not source.is_file():blockers.append('source-unavailable')
    blockers.extend('missing-runtime:'+x for x in missing)
    if kind=='provider':blockers.append('provider-not-probed')
    if kind=='inspection':blockers.append('media-viewing-or-listening-not-yet-performed')
    if kind=='implementation':blockers.append('target-stack-and-browser-not-yet-verified')
    state='ready-for-local-action' if not blockers else 'preparation-available'
    if kind=='text' and not blockers:state='ready-for-text-work'
    if kind=='handoff' and not blockers:state='ready-for-manual-editor-handoff'
    fallback={
      'text':'Use supplied content and current locks; complete the requested text artifact.',
      'file':'Preserve the source; inspect schema or provide exact local steps. Run only the available supported operation.',
      'provider':'Finish the prompt/specification and asset-role map now. Check the real connected provider before actual generation.',
      'handoff':'Complete a manual Jianying/CapCut edit decision list, source manifest, subtitles when requested, and export checklist. Do not install, probe or invoke a Jianying/CapCut CLI; do not claim the editor project was modified or exported.',
      'inspection':'Review supplied text/frames only to their evidence limits. Do not issue a full media pass without inspection.',
      'implementation':'Produce the requested design/code in the existing stack; report actual browser/runtime coverage separately.',
    }[kind]
    return {'task':task,'module':module,'kind':kind,'state':state,
            'input':{'supplied':source is not None,'file_exists':bool(source and source.is_file())},
            'dependencies':dependencies,'blockers':blockers,'continue_now':fallback,
            'guarantee':'No external-provider readiness, host access, media quality or global optimum inferred.'}


def require_file(value):
    path=Path(value).expanduser().resolve()
    if not path.is_file():raise ValueError('Input file unavailable')
    return path


def require_new_output(value,inputs):
    path=Path(value).expanduser().resolve()
    if path in inputs or path.exists() or path.with_suffix('.txt').exists():
        raise ValueError('Output or companion already exists / overlaps input; choose a new output')
    path.parent.mkdir(parents=True,exist_ok=True)
    return path


def run_helper(args):
    root=find_root(args.plugin_root);source=require_file(args.input)
    if args.command in {'lines-check','lines-export'}:
        helper=root/'skills/aigc-sound/scripts/storyboard_lines/build_lines_doc.py'
        review=require_file(args.review) if args.command=='lines-export' else None
        if args.command=='lines-export' and not args.confirmed:
            raise ValueError('Export requires a genuine confirmed/no-change plan; --confirmed is only a record, not permission')
        inputs={source}|({review} if review else set())
        output=require_new_output(args.output,inputs)
        cmd=[sys.executable,str(helper),str(source),'--mode','check' if args.command=='lines-check' else 'extract',
             '--language',args.language,'--output',str(output)]
        if args.episodes:cmd+=['--episodes',args.episodes]
        if args.sheet:cmd+=['--sheet',args.sheet]
        if args.strip_speakers:cmd+=['--strip-speakers']
        if review:cmd+=['--review',str(review),'--confirmed']
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        if result.returncode:raise ValueError(result.stderr.strip())
        return {'status':'local-helper-completed','operation':args.command,'output':str(output),'external_publish':False}
    if args.command=='review-ledger':
        helper=root/'skills/aigc-review/scripts/prompt_review_checks.py'
        result=subprocess.run([sys.executable,str(helper),args.mode,'--input',str(source),'--json'],capture_output=True,text=True,timeout=60)
        try:payload=json.loads(result.stdout)
        except json.JSONDecodeError:raise ValueError('Reviewer did not return valid JSON')
        # The helper may exit 0 for judgment-needed or not-triggered; preserve
        # its actual semantic status rather than reporting a media pass.
        return {'operation':'review-ledger','helper_exit_code':result.returncode,'result':payload,
                'scope':'Extracted ledger only; not raw-text extraction or generated-media validation.'}
    if args.command=='probe-media':
        binary=shutil.which('ffprobe')
        if not binary:raise ValueError('ffprobe unavailable; media file not technically inspected')
        result=subprocess.run([binary,'-v','error','-show_entries','format=duration,format_name:stream=codec_type,codec_name,width,height,sample_rate,channels',
                               '-of','json',str(source)],capture_output=True,text=True,timeout=60)
        if result.returncode:raise ValueError('ffprobe could not inspect the source')
        return {'operation':'probe-media','metadata':json.loads(result.stdout),'scope':'Technical metadata only, no perceptual QC.'}
    raise ValueError('Unsupported helper')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('preflight');p.add_argument('--task',choices=sorted(TASKS),required=True);p.add_argument('--input')
    for name in ['lines-check','lines-export','review-ledger','probe-media']:
        p=sub.add_parser(name);p.add_argument('--plugin-root');p.add_argument('--input',required=True)
        if name.startswith('lines-'):
            p.add_argument('--output',required=True);p.add_argument('--language',choices=['en','pt-BR','es-MX','unknown'],default='unknown')
            p.add_argument('--episodes');p.add_argument('--sheet');p.add_argument('--strip-speakers',action='store_true')
            if name=='lines-export':p.add_argument('--review',required=True);p.add_argument('--confirmed',action='store_true')
        if name=='review-ledger':p.add_argument('--mode',choices=['dialogue','handoff','minimal-diff','visual-only'],required=True)
    args=parser.parse_args()
    try:
        result=preflight(args.task,args.input) if args.command=='preflight' else run_helper(args)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status':'not-executed','reason':str(exc),'continue_now':'Preserve originals and complete independent text/preparation work.'},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__=='__main__':raise SystemExit(main())
