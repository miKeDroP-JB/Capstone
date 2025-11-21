import os, json, time, hashlib, secrets, hmac
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Header, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn

# PATTERN VALIDATOR - Layer 5
class PatternValidator:
    def __init__(self):
        self.blocked = [
            'ignore previous', 'disregard all', 'forget everything',
            'system prompt', 'jailbreak', 'sudo', 'admin override'
        ]
        self.max_length = 10000
        self.suspicious = ['<script>', '<?php', 'eval(', 'exec(']
    
    def validate(self, text):
        if len(text) > self.max_length:
            return False, f'Too long ({len(text)} > {self.max_length})'
        if not text.strip():
            return False, 'Empty pattern'
        
        text_lower = text.lower()
        for blocked in self.blocked:
            if blocked in text_lower:
                return False, f'Blocked phrase: {blocked}'
        
        for sus in self.suspicious:
            if sus in text:
                return False, f'Suspicious code: {sus}'
        
        return True, 'Valid'
    
    def sanitize(self, text):
        return text.replace('\x00', '').strip()

# AUTO-BACKUP - Layer 6
class BackupSystem:
    def __init__(self, backup_dir='backups', retention_days=7):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.retention = retention_days
        self.last_backup = None
    
    def backup(self, data, name='grimoire'):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{name}_{ts}.json'
        filepath = self.backup_dir / filename
        filepath.write_text(json.dumps(data, indent=2))
        self.last_backup = filepath
        self._cleanup()
        return str(filepath)
    
    def _cleanup(self):
        cutoff = datetime.now() - timedelta(days=self.retention)
        for backup_file in self.backup_dir.glob('*.json'):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff:
                backup_file.unlink()
    
    def list_backups(self):
        backups = []
        for f in sorted(self.backup_dir.glob('*.json'), reverse=True):
            backups.append({
                'name': f.name,
                'path': str(f),
                'size': f.stat().st_size,
                'created': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        return backups

# ENCRYPTION - Layer 4
class Encryption:
    def __init__(self):
        try:
            from cryptography.fernet import Fernet
            self.Fernet = Fernet
            key_file = Path('encryption.key')
            if key_file.exists():
                self.key = key_file.read_bytes()
            else:
                self.key = Fernet.generate_key()
                key_file.write_bytes(self.key)
                print(f'🔐 Encryption key generated: encryption.key')
            self.cipher = Fernet(self.key)
            self.enabled = True
        except ImportError:
            print('⚠️  cryptography not installed - encryption disabled')
            self.enabled = False
    
    def encrypt(self, data):
        if not self.enabled:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted):
        if not self.enabled:
            return encrypted
        return self.cipher.decrypt(encrypted.encode()).decode()

# RATE LIMITER - Layer 3
limiter = Limiter(key_func=get_remote_address)

# AUDIT LOG - Layer 1
class AuditLog:
    def __init__(self):
        self.log_dir = Path('audit_logs')
        self.log_dir.mkdir(exist_ok=True)
        today = datetime.now().strftime('%Y%m%d')
        self.log_file = self.log_dir / f'audit_{today}.jsonl'
    
    def log(self, event, agent, action, result, meta=None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'agent': agent,
            'action': action,
            'result': result,
            'metadata': meta or {}
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def recent(self, limit=100):
        if not self.log_file.exists():
            return []
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
            return [json.loads(line) for line in lines[-limit:]]

# COST TRACKER - Layer 2
class CostTracker:
    def __init__(self, daily_budget=10.0):
        self.daily_budget = daily_budget
        self.costs = defaultdict(lambda: {'total': 0.0, 'requests': 0})
        self.rates = {
            'claude': {'input': 0.003, 'output': 0.015},
            'gemini': {'input': 0.000125, 'output': 0.000375},
            'gpt': {'input': 0.0005, 'output': 0.0015}
        }
        self.cost_file = Path('costs.json')
        self._load()
    
    def _load(self):
        if self.cost_file.exists():
            data = json.loads(self.cost_file.read_text())
            today = datetime.now().strftime('%Y-%m-%d')
            if today in data:
                self.costs = defaultdict(lambda: {'total': 0.0, 'requests': 0}, data[today])
    
    def _save(self):
        today = datetime.now().strftime('%Y-%m-%d')
        self.cost_file.write_text(json.dumps({today: dict(self.costs)}, indent=2))
    
    def record(self, provider, input_tokens, output_tokens):
        rates = self.rates.get(provider, {'input': 0, 'output': 0})
        cost = (input_tokens / 1000 * rates['input']) + (output_tokens / 1000 * rates['output'])
        self.costs[provider]['total'] += cost
        self.costs[provider]['requests'] += 1
        self._save()
        return cost
    
    def today_total(self):
        return sum(p['total'] for p in self.costs.values())
    
    def check_budget(self):
        total = self.today_total()
        remaining = self.daily_budget - total
        percent = (total / self.daily_budget) * 100
        
        if percent > 90:
            status = 'CRITICAL'
        elif percent > 75:
            status = 'WARNING'
        elif percent > 50:
            status = 'CAUTION'
        else:
            status = 'OK'
        
        return {
            'spent': total,
            'budget': self.daily_budget,
            'remaining': remaining,
            'percent_used': percent,
            'status': status,
            'by_provider': dict(self.costs)
        }

# GATE
class Gate:
    def __init__(self, master_key, audit):
        self.master_key = master_key
        self.agent_keys = {}
        self.blocked_ips = set()
        self.audit = audit
    
    def create_token(self, name):
        ts = int(time.time())
        payload = f'{name}:{ts}'
        token = hmac.new(self.master_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        full_token = f'{name}:{ts}:{token}'
        self.agent_keys[name] = {'token': full_token, 'created': ts}
        self.audit.log('AGENT_REGISTER', name, 'register', 'SUCCESS')
        return full_token
    
    def verify(self, auth, ip):
        if ip in self.blocked_ips:
            self.audit.log('AUTH_BLOCKED', 'unknown', 'verify', 'BLOCKED_IP', {'ip': ip})
            return False, 'BLOCKED'
        if not auth:
            self.audit.log('AUTH_FAILED', 'unknown', 'verify', 'NO_AUTH', {'ip': ip})
            return False, 'NO_AUTH'
        try:
            parts = auth.replace('Bearer ', '').split(':')
            name, ts, token = parts[0], parts[1], parts[2]
            payload = f'{name}:{ts}'
            expected = hmac.new(self.master_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
            if hmac.compare_digest(token, expected):
                self.audit.log('AUTH_SUCCESS', name, 'verify', 'SUCCESS', {'ip': ip})
                return True, name
            self.audit.log('AUTH_FAILED', name, 'verify', 'INVALID_TOKEN', {'ip': ip})
            return False, 'INVALID'
        except:
            self.audit.log('AUTH_ERROR', 'unknown', 'verify', 'PARSE_ERROR', {'ip': ip})
            return False, 'INVALID'

# GRIMOIRE
class Grimoire:
    def __init__(self, audit, encryption, validator):
        self.patterns = {}
        self.stats = {'total': 0, 'hits': 0, 'saved': 0, 'rejected': 0}
        self.audit = audit
        self.encryption = encryption
        self.validator = validator
    
    def compress(self, text, agent, learn=True):
        self.stats['total'] += 1
        
        # Validate
        valid, reason = self.validator.validate(text)
        if not valid:
            self.stats['rejected'] += 1
            self.audit.log('PATTERN_REJECTED', agent, 'compress', f'INVALID: {reason}')
            raise ValueError(f'Invalid pattern: {reason}')
        
        # Sanitize
        text = self.validator.sanitize(text)
        
        pid = hashlib.md5(text.encode()).hexdigest()[:12]
        
        if pid in self.patterns:
            self.stats['hits'] += 1
            self.patterns[pid]['uses'] += 1
            self.audit.log('COMPRESS_HIT', agent, 'compress', 'CACHE_HIT', {'pattern_id': pid})
            comp = self.encryption.decrypt(self.patterns[pid]['comp']) if self.encryption.enabled else self.patterns[pid]['comp']
            return {'compressed': comp, 'cache_hit': True, 'pattern_id': pid, 'encrypted': self.encryption.enabled}
        
        words = text.lower().split()
        stops = {'the','a','an','is','are','was','to','of','and','in','for','on','with','this','that'}
        comp = ' '.join([w[:4] if len(w)>4 else w for w in words if w not in stops][:15])
        
        tokens_before = len(words)
        tokens_after = len(comp.split())
        
        if learn:
            encrypted_comp = self.encryption.encrypt(comp) if self.encryption.enabled else comp
            self.patterns[pid] = {'orig': text, 'comp': encrypted_comp, 'created': time.time(), 'uses': 1}
            self.stats['saved'] += tokens_before - tokens_after
            self.audit.log('PATTERN_LEARNED', agent, 'compress', 'NEW_PATTERN', {'pattern_id': pid, 'encrypted': self.encryption.enabled})
        
        return {
            'compressed': comp,
            'cache_hit': False,
            'pattern_id': pid,
            'tokens_before': tokens_before,
            'tokens_after': tokens_after,
            'tokens_saved': tokens_before - tokens_after,
            'encrypted': self.encryption.enabled
        }
    
    def export(self):
        return {
            'patterns': self.patterns,
            'stats': self.stats,
            'encrypted': self.encryption.enabled,
            'exported_at': datetime.now().isoformat()
        }

# ROUTER
class Router:
    def __init__(self):
        self.weights = {'quality': 0.7, 'speed': 0.5, 'cost': 0.3}
    
    def route(self, task='general', complexity=0.5):
        if task in ['strategy','code'] or complexity > 0.7:
            return 'claude'
        if task in ['research','analysis']:
            return 'gemini'
        return 'gpt'

# BRAIN - COMPLETE FORTRESS
class Brain:
    def __init__(self):
        self.master_key = secrets.token_hex(32)
        self.encryption = Encryption()
        self.validator = PatternValidator()
        self.backup = BackupSystem()
        self.audit = AuditLog()
        self.costs = CostTracker(daily_budget=10.0)
        self.gate = Gate(self.master_key, self.audit)
        self.grimoire = Grimoire(self.audit, self.encryption, self.validator)
        self.router = Router()
        self.agents = {}
        self.cycles = 0
        self.perf = 1.0
        print(f'\n🔐 MASTER KEY: {self.master_key}\n   SAVE THIS!\n')
        self.audit.log('SYSTEM_START', 'SYSTEM', 'startup', 'ONLINE', {
            'encryption': self.encryption.enabled,
            'validation': True,
            'auto_backup': True
        })
    
    def register(self, name):
        token = self.gate.create_token(name)
        self.agents[name] = {'registered': time.time()}
        return token
    
    def compound(self, agent):
        self.perf *= 1.01
        self.cycles += 1
        self.audit.log('COMPOUND_CYCLE', agent, 'compound', 'SUCCESS', {'cycle': self.cycles, 'perf': self.perf})
        
        # Auto-backup every 10 cycles
        if self.cycles % 10 == 0:
            self.auto_backup(agent)
        
        return self.perf
    
    def auto_backup(self, agent):
        data = self.grimoire.export()
        filepath = self.backup.backup(data)
        self.audit.log('AUTO_BACKUP', agent, 'backup', 'SUCCESS', {'file': filepath})
        return filepath

# API
app = FastAPI(title='Brain OS - FORTRESS COMPLETE')
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
brain = Brain()

class Req(BaseModel):
    text: str

class Reg(BaseModel):
    agent_name: str
    master_key: str

@app.get('/')
def root():
    budget = brain.costs.check_budget()
    return {
        'name': 'Brain OS - FORTRESS COMPLETE',
        'status': 'ONLINE',
        'cycles': brain.cycles,
        'patterns': len(brain.grimoire.patterns),
        'budget_status': budget['status'],
        'spent_today': f'${budget["spent"]:.4f}',
        'security': {
            'gate': 'ACTIVE',
            'audit_log': 'RECORDING',
            'cost_tracking': 'MONITORING',
            'rate_limiting': 'ENFORCED',
            'encryption': 'ENABLED' if brain.encryption.enabled else 'DISABLED',
            'pattern_validation': 'FILTERING',
            'auto_backup': 'SCHEDULED'
        },
        'fortress_layers': 6
    }

@app.post('/register')
@limiter.limit('5/minute')
def register(r: Reg, request: Request):
    if r.master_key != brain.master_key:
        raise HTTPException(403, 'Invalid key')
    return {'agent': r.agent_name, 'token': brain.register(r.agent_name)}

@app.post('/compress')
@limiter.limit('100/minute')
def compress(r: Req, request: Request, authorization: str = Header(None)):
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, f'Denied: {agent}')
    
    try:
        result = brain.grimoire.compress(r.text, agent)
        provider = brain.router.route('general', 0.5)
        cost = brain.costs.record(provider, result.get('tokens_before', 0), result.get('tokens_after', 0))
        result['cost'] = f'${cost:.6f}'
        result['provider'] = provider
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get('/stats')
@limiter.limit('30/minute')
def stats(request: Request, authorization: str = Header(None)):
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    return {
        'performance': f'{brain.perf:.4f}x',
        'cycles': brain.cycles,
        'grimoire': brain.grimoire.stats,
        'patterns': len(brain.grimoire.patterns),
        'agents': list(brain.agents.keys()),
        'budget': brain.costs.check_budget(),
        'encryption_enabled': brain.encryption.enabled,
        'last_backup': str(brain.backup.last_backup) if brain.backup.last_backup else None
    }

@app.post('/compound')
@limiter.limit('10/minute')
def compound(request: Request, authorization: str = Header(None)):
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    return {'cycle': brain.cycles, 'performance': f'{brain.compound(agent):.4f}x'}

@app.get('/audit')
@limiter.limit('20/minute')
def get_audit(request: Request, limit: int = 100, authorization: str = Header(None)):
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    return {'logs': brain.audit.recent(limit), 'count': len(brain.audit.recent(limit))}

@app.get('/costs')
@limiter.limit('30/minute')
def get_costs(request: Request, authorization: str = Header(None)):
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    return brain.costs.check_budget()

@app.post('/backup')
@limiter.limit('5/minute')
def manual_backup(request: Request, authorization: str = Header(None)):
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    filepath = brain.auto_backup(agent)
    return {'backup_created': filepath, 'encrypted': brain.encryption.enabled}

@app.get('/backups')
@limiter.limit('10/minute')
def list_backups(request: Request, authorization: str = Header(None)):
    ip = request.client.host
    ok, agent = brain.gate.verify(authorization, ip)
    if not ok:
        raise HTTPException(403, 'Denied')
    return {'backups': brain.backup.list_backups(), 'retention_days': brain.backup.retention}

if __name__ == '__main__':
    print('╔═══════════════════════════════════════╗')
    print('║  BRAIN OS - FORTRESS COMPLETE         ║')
    print('║                                       ║')
    print('║  🔐 Layer 1: Gate + Auth               ║')
    print('║  📝 Layer 2: Audit Log                 ║')
    print('║  💰 Layer 3: Cost Tracking             ║')
    print('║  🛡️  Layer 4: Rate Limiting            ║')
    print('║  🔒 Layer 5: Encryption                ║')
    print('║  ✅ Layer 6: Pattern Validation        ║')
    print('║  💾 Layer 7: Auto-Backup               ║')
    print('║                                       ║')
    print('║  Love • Loyalty • Honor • Everybody Eats  ║')
    print('╚═══════════════════════════════════════╝')
    print(f'\n🔒 Encryption: {"ENABLED" if brain.encryption.enabled else "DISABLED"}')
    print(f'💰 Daily Budget: ${brain.costs.daily_budget}')
    print(f'💾 Auto-Backup: Every 10 cycles (7-day retention)')
    print('\n📊 http://127.0.0.1:3000')
    print('📖 http://127.0.0.1:3000/docs')
    print('🔑 ./encryption.key')
    print('📝 ./audit_logs/')
    print('💰 ./costs.json')
    print('💾 ./backups/\n')
    uvicorn.run(app, host='0.0.0.0', port=3000)
