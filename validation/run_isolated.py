"""Run third-party validation in disposable homes without passing agent credentials."""
import argparse,json,os,pathlib,subprocess,sys,time
from datetime import datetime, timezone, timedelta
parser=argparse.ArgumentParser();parser.add_argument('name');parser.add_argument('--python',required=True);parser.add_argument('--cwd',required=True);parser.add_argument('command',nargs=argparse.REMAINDER);args=parser.parse_args()
root=pathlib.Path(__file__).resolve().parent
scratch=pathlib.Path(os.environ.get('VALIDATION_SCRATCH_DIR',str(root.parent.parent/'work'/'ai-validation'/'reproduction')))
sandbox=scratch/'sandboxes'/args.name;sandbox.mkdir(parents=True,exist_ok=True)
home=sandbox/'home';temp=sandbox/'tmp';guard=root/'offline-guard'
for d in [home,temp,guard,home/'AppData'/'Roaming',home/'AppData'/'Local'] :d.mkdir(parents=True,exist_ok=True)
env=os.environ.copy()
for key in list(env):
    if any(s in key.upper() for s in ['TOKEN','SECRET','PASSWORD','API_KEY','OPENAI','ANTHROPIC','AZURE','GEMINI','AWS_']):env.pop(key,None)
for key in ['HOME','USERPROFILE']:env[key]=str(home)
for key in ['TEMP','TMP','TMPDIR']:env[key]=str(temp)
env.update({'APPDATA':str(home/'AppData'/'Roaming'),'LOCALAPPDATA':str(home/'AppData'/'Local'),'XDG_CACHE_HOME':str(home/'cache'),'XDG_CONFIG_HOME':str(home/'config'),'CODEX_HOME':str(home/'.codex'),'CLAUDE_CONFIG_DIR':str(home/'.claude'),'GH_CONFIG_DIR':str(home/'gh'),'TOKENECONOMIZER_HOME':str(home/'tokeneconomizer'),'NANOCHAT_BASE_DIR':str(home/'nanochat'),'HF_HOME':str(home/'hf'),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','WANDB_MODE':'disabled','WANDB_DISABLED':'true','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','GIT_TERMINAL_PROMPT':'0','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':str(home/'.gitconfig'),'NO_PROXY':'localhost,127.0.0.1,::1','HTTP_PROXY':'http://127.0.0.1:9','HTTPS_PROXY':'http://127.0.0.1:9','ALL_PROXY':'http://127.0.0.1:9','COLUMNS':'160','TE_CODEX_E2E':'0','TE_OPENCODE_E2E':'0'})
# Auditing supplements the upstream test mocks; it isn't an OS security boundary.
env['PYTHONPATH']=str(guard)+os.pathsep+str(pathlib.Path(args.cwd).resolve())
git_bash=pathlib.Path(os.environ.get('VALIDATION_GIT_BASH_DIR','D:/Git/Git/bin'))
if (git_bash/'bash.exe').exists():
    env['PATH']=str(git_bash)+os.pathsep+str(pathlib.Path(args.python).resolve().parent)+os.pathsep+env.get('PATH','')
env['VALIDATION_NETWORK_LOG']=str(sandbox/'blocked-network.jsonl')
command=[str(pathlib.Path(args.python).resolve()),*args.command]
(root/'logs').mkdir(parents=True,exist_ok=True)
log=root/'logs'/(args.name+'.log');start=time.monotonic()
print('Isolated run:',args.name,'log:',log,flush=True)
with log.open('w',encoding='utf-8') as output:
    process=subprocess.Popen(command,cwd=args.cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    for line in process.stdout:
        output.write(line);output.flush();print(line,end='',flush=True)
    rc=process.wait()
summary={'name':args.name,'started_with_sanitized_environment':True,'command':command,'cwd':str(pathlib.Path(args.cwd).resolve()),'exit_code':rc,'elapsed_seconds':round(time.monotonic()-start,2),'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'log':str(log),'isolation':'Dedicated venv and redirected home/config/tmp, no inherited API secrets, offline env, Python socket guard. Not an OS sandbox.'}
(root/'logs'/(args.name+'-run.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raise SystemExit(rc)
